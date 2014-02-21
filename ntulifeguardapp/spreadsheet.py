#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib2
import logging
import gdata
import gdata.spreadsheet.service
from apiclient.discovery import build
try:
    from oauth2client.client import SignedJwtAssertionCredentials
except ImportError:
    pass

logger = logging.getLogger(__name__)
#
SERVICE_ACCOUNT_EMAIL = '1005762717201-rp7kbtccb0nqc97oh369atni4seu4v62@developer.gserviceaccount.com'
SERVICE_ACCOUNT_PEM_FILE_PATH = 'ntulifeguardapp-privatekey.pem'

def createDriveService():
    f = file(SERVICE_ACCOUNT_PEM_FILE_PATH, 'rb')
    key = f.read()
    f.close()
    try:
        credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL, key, scope=['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive.appdata'])
    except NameError:
        return None
    else:
        http = httplib2.Http()
        http = credentials.authorize(http)

        return build('drive', 'v2', http=http)

   

def buildSpreadsheetService():
    f = file(SERVICE_ACCOUNT_PEM_FILE_PATH, 'rb')
    key = f.read()
    f.close()   
    scope = 'https://spreadsheets.google.com/feeds'

    try:
        credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT_EMAIL, key, scope)
    except NameError:
        return None
    else:
        http = httplib2.Http()
        http = credentials.authorize(http)
        build('drive', 'v2', http=http)
        sheets = gdata.spreadsheet.service.SpreadsheetsService()
        sheets.additional_headers = {'Authorization': 'Bearer %s' % http.request.credentials.access_token}

        return sheets
