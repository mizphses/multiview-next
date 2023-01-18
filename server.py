from flask import Flask, render_template, request, redirect, url_for, session
from converter import downloader, login

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# Spreadsheets API
from googleapiclient import discovery

import os
import sys

sys.setrecursionlimit(10000)

app = Flask(__name__)
app.secret = 'secret'


@app.route('/')
def index():
    if os.path.exists('token.json'):
        auth = True
    else:
        auth = False
    return render_template('index.html', auth = auth)

@app.route('/login')
def loginpage():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
    if os.path.exists('token.json'):
        return redirect(url_for('index'))
    else:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if os.path.exists('token.json'):
        os.remove('token.json')
    return redirect(url_for('index'))

@app.route('/create', methods=['POST'])
def create():
    if os.path.exists('token.json'):
        auth = True
    else:
        auth = False
    creds = login()
    service = discovery.build('sheets', 'v4', credentials=creds)
    file_url = request.form['file_url']
    file_id = file_url[39:-17]
    sheet = service.spreadsheets().values().get(spreadsheetId=file_id, range='A1:B1000').execute()['values']
    del sheet[0]
    htmls = []
    for i in range(len(sheet)):
        htmls.append([downloader(login(), sheet[i][1][40:-12]), sheet[i][0], sheet[i][1]])
    return render_template('views.html', htmls = htmls, auth = auth)

if __name__ == '__main__':
    app.run(host="localhost", debug=False, port=50000)
