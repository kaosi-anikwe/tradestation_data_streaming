import os
import gspread
import requests
from typing import Any
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from . import logger

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
google_credentials_file = os.getenv("CREDENTIALS_FILE")
spreadsheet_id = os.getenv("SPREADSHEET_ID")

# Set up the scope for accessing Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# Authenticate with Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_file, scope)
client = gspread.authorize(creds)
# get spreadsheet
spreadsheet = client.open_by_key(spreadsheet_id)


def get_access_token():
    auth_url = "https://signin.tradestation.com/oauth/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    logger.info("Sending request for access token...")
    response = requests.post(auth_url, headers=headers, data=payload)

    if response.status_code == 200:
        return str(response.json().get("access_token"))
    else:
        logger.warning("Failed to obtain access token.")
        raise Exception("Failed to obtain access token.")


def update_spreadsheet(task: str, data: Any, spreadsheet=spreadsheet):
    print(data)
    logger.info("Quote data sent to spreadsheet.")
