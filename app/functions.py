import os
import copy
import gspread
import requests
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
    """Retrieves access token for authenticating requests."""
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


def flatten_dict(d, parent_key="", sep="_"):
    """Flattens `dict` to key-value pairs with no nested dicts or lists."""
    items = {}
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.update(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep))
                else:
                    items[f"{new_key}{sep}{i}"] = item
        else:
            items[new_key] = value
    return items


def update_spreadsheet(task: str, data: dict, spreadsheet=spreadsheet):
    """Update Google spreadsheet based on task type."""
    # Get worksheet
    if task not in [worksheet.title for worksheet in spreadsheet.worksheets()]:
        worksheet = spreadsheet.add_worksheet(task, rows=100, cols=20)
    else:
        worksheet = spreadsheet.worksheet(task)

    if task == "Quotes":
        try:
            # Load existing data from the sheet
            existing_data = worksheet.get_all_records()
        except:
            # Handle exceptions as needed
            existing_data = []

        data = flatten_dict(data)
        new_data = []

        if existing_data:
            # Get current symbol being processed
            symbol = data.get("Symbol")
            new_header = copy.deepcopy(existing_data[0])
            # Update header with new data
            new_header.update(data)
            header = list(new_header.keys())
            # Add list of header values
            new_data.append(header)
            added_records = []  # keeping track of added records
            for d in existing_data:
                if d.get("Symbol") == symbol:
                    # Update record with incoming data
                    record = copy.deepcopy(d)
                    record.update(data)
                    new_data.append([record.get(key, "") for key in header])
                    added_records.append(record.get("Symbol"))
                else:
                    new_data.append([d.get(key, "") for key in header])
                    added_records.append(d.get("Symbol"))
            new_data.append([data.get(key, "") for key in header]) if data.get(
                "Symbol"
            ) not in added_records else None
        else:
            header = list(data.keys())
            new_data.append(header)
            new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        worksheet.update(new_data)

    elif task == "Bars":
        new_data = []
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        worksheet.update(new_data)

    elif task == "Positions":
        new_data = []
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        worksheet.update(new_data)

    elif task == "Orders":
        new_data = []
        data = flatten_dict(data)
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        worksheet.update(new_data)

    logger.info(f"Spreadsheet updated with {task} data.")
