import os
from base64 import b64encode
from http import HTTPStatus

from functools import wraps
from flask import Flask, render_template, current_app, session, redirect, request, g

from client import OIDCClient

app = Flask(__name__)

app.secret_key = b64encode(os.urandom(32))

with app.app_context():
  current_app.oidc_client = OIDCClient(os.getenv('ISSUER_BASE_URL'), 
                      os.getenv('CLIENT_ID'), 
                      os.getenv('CLIENT_SECRET'), 
                      os.getenv('REDIRECT_URI'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_redirect():
    nonce = b64encode(os.urandom(32)).decode()
    state = b64encode(os.urandom(32)).decode()

    session['nonce'] = nonce
    session['state'] = state

    auth_url = current_app.oidc_client.auth_url(state, scope=['openid', 'profile', 'email'], nonce = nonce)

    return redirect(auth_url)

@app.route('/callback')
def handle_callback():
    code = request.args.get('code', '')
    if code == '':
      return 'bad or missing code', HTTPStatus.BAD_REQUEST

    state = request.args.get('state', '')
    if session.get('state', '') == '' or session['state'] != state:
        return 'bad state', HTTPStatus.BAD_REQUEST

    session.pop('state')


    tokens = current_app.oidc_client.exchange_token(code)

    saved_nonce = session['nonce']

    id_token = current_app.oidc_client.decode(tokens.id_token, nonce=saved_nonce)

    logout_redirect = os.getenv('PUBLIC_URL', 'https://localhost')
    logout_url = current_app.oidc_client.end_session_endpoint + '?id_token_hint=' +  tokens.id_token + '&post_logout_redirect_uri=' + logout_redirect

    return render_template('post_callback.html', name=id_token['name'], access_token=tokens.access_token, logout_url=logout_url)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      tok = request.headers.get('Authorization', '')
      if 'Bearer ' not in tok:
        return 'missing authorization header', HTTPStatus.UNAUTHORIZED

      token = tok.replace('Bearer ', '')

      nonoce = session.get('nonce', '')

      try:
        access_token = current_app.oidc_client.decode(token, nonce = nonoce)
        g.access_token = access_token
      except Exception as e:
          return str(e), HTTPStatus.UNAUTHORIZED
      
      return f(*args, **kwargs)
    return decorated_function

def scopes_required(scopes):
  def wrapd_function(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if g.access_token == None:
        return 'missing token', HTTPStatus.UNAUTHORIZED

      if len(set(g.access_token.get('scp', [])).intersection(scopes)) == 0:
        return 'missing scopes', HTTPStatus.FORBIDDEN

      return f(*args, **kwargs)
    return decorated_function
  return wrapd_function

@app.route('/protected')
@token_required
@scopes_required(['profile'])
def protected():
  return 'you are authorized'
