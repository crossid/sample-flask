# Readme

First run to install dependancies

```bash
pip install -r requirements.txt
```

Then you can run the server with

```bash
CLIENT_ID=<client_id>\
CLIENT_SECRET=<client_secret> \
REDIRECT_URI=https://localhost/callback \
ISSUER_BASE_URL=https://<tenant_id>.crossid.io/oauth2/ \
flask app.py
```


## Deploying on Digital Ocean

Click this button to deploy the app to the DigitalOcean App Platform.

[![Deploy to DigitalOcean](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/crossid/sample-flask/tree/main)

or if you have `doctl` installed then run:

`doctl apps create --spec .do/app.yaml`
