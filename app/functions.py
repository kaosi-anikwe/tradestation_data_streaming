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


def update_spreadsheet(task: str, data: dict, spreadsheet=spreadsheet):
    print(data)
    
    # get worksheet
    if task not in [worksheet.title for worksheet in spreadsheet.worksheets()]:
        worksheet = spreadsheet.add_worksheet(task, rows=100, cols=20)
    else:
        worksheet = spreadsheet.worksheet(task)

    try:
        # Load existing data from the sheet
        existing_data = worksheet.get_all_records()
    except:
        # Handle exceptions as needed
        existing_data = []
    

    # Remove unwanted fields
    del data["MarketFlags"]
    # Process the incoming JSON data and extract key-value pairs
    symbol = data.get("Symbol")

    header = data.keys()
    # If the sheet is empty, create a new header row
    if not existing_data:
        existing_data.append(list(header))
    else:
        existing_data[0] = list(header)



    # Convert existing_data to a list of dictionaries
    existing_data = list(existing_data)

    # Check if data for the symbol already exists in the sheet
    symbol_data = next((row for row in existing_data if symbol in row), None)

    # If data for the symbol doesn't exist, create a new row
    if symbol_data is None:
        row = [data.get(header, "") for header in header]
        existing_data.append(row)
    # If data for the symbol exists, update the existing row
    else:
        for key, value in data.items():
            symbol_data[key] = value

    # Update the entire worksheet with the updated data
    # worksheet.update([existing_data[0]] + [list(row.values()) for row in existing_data])
    logger.info(existing_data)
    worksheet.update(existing_data)


    logger.info(f"Spreadsheet updated with {task} data.")
