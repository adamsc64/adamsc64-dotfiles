#!/usr/bin/env python3
"""
gdoc2md.py: Download a Google Doc as Markdown via Drive API.
Usage: gdoc2md.py <google-doc-url>
Example:
  gdoc2md.py https://docs.google.com/document/d/1m7UNHEdvnQ2Jvua-sujBUuVLA3nY5PO9EqZ5OO2qNfQ/edit
"""
import os
import sys
import re
import requests
from os.path import expanduser
from google_auth_oauthlib.flow import InstalledAppFlow

# Config
CLIENT_SECRET_FILE = expanduser('~/.config/google-oauth/client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def extract_id(url):
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if not m:
        sys.exit('Error: could not parse document ID from URL')
    return m.group(1)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    doc_url = sys.argv[1]
    doc_id = extract_id(doc_url)

    # OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    # Export
    export_url = f'https://www.googleapis.com/drive/v3/files/{doc_id}/export'
    params = {'mimeType': 'text/markdown'}
    headers = {'Authorization': f'Bearer {creds.token}'}
    resp = requests.get(export_url, params=params, headers=headers)
    if not resp.ok:
        sys.exit(f'Error {resp.status_code}: {resp.text}')
    resp.raise_for_status()

    out_file = f'{doc_id}.md'
    with open(out_file, 'wb') as f:
        f.write(resp.content)
    print(f'Saved Markdown to {out_file}')


if __name__ == '__main__':
    main()
