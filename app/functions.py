import os
import copy
import time
import json
import gspread
import requests
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from . import logger

load_dotenv()

spreadsheet_id = os.getenv("SPREADSHEET_ID")
google_credentials_file = os.getenv("CREDENTIALS_FILE")

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


def get_parameters():
    with open("parameters.json", "r") as file:
        parameters = json.load(file)
    return parameters


def sort_dict(data, first):
    first_value = data.pop(first)
    # Sort the remaining key-value pairs alphabetically
    sorted_dict = {key: data[key] for key in sorted(data)}
    # Add the specific key-value pair at the beginning
    sorted_dict = {first: first_value, **sorted_dict}
    return sorted_dict


def get_access_token():
    """Retrieves access token for authenticating requests."""
    auth_url = "https://signin.tradestation.com/oauth/token"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    parameters = get_parameters()
    payload = {
        "grant_type": "refresh_token",
        "client_id": parameters["CLIENT_ID"],
        "client_secret": parameters["CLIENT_SECRET"],
        "refresh_token": parameters["REFRESH_TOKEN"],
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


def remove_duplicates(input_dict):
    """Removes duplicates from a dictionary by preserving the last occurrence of each key."""
    unique_dict = {}  # Create a new dictionary to store unique key-value pairs

    for key, value in input_dict.items():
        if key not in unique_dict:
            unique_dict[key] = value  # Add the key-value pair to the unique dictionary

    return unique_dict


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
            # Sort header alphabetically
            new_header = sort_dict(new_header, "Symbol")
            header = list(new_header.keys())
            # Add list of header values
            new_data.append(header)
            added_records = []  # keeping track of added records
            for d in existing_data:
                if d.get("Symbol") == symbol:
                    # Update record with incoming data
                    record = copy.deepcopy(d)
                    record.update(data)
                    record = remove_duplicates(record)
                    new_data.append(
                        [record.get(key, "") for key in header]
                    ) if record.get("Symbol") not in added_records else None
                    added_records.append(record.get("Symbol"))
                else:
                    new_data.append([d.get(key, "") for key in header]) if d.get(
                        "Symbol"
                    ) not in added_records else None
                    added_records.append(d.get("Symbol"))
            new_data.append([data.get(key, "") for key in header]) if data.get(
                "Symbol"
            ) not in added_records else None
        else:
            header = list(data.keys())
            new_data.append(header)
            new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        time.sleep(2)
        worksheet.update(new_data)

    elif task == "Bars":
        new_data = []
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        time.sleep(2)
        worksheet.update(new_data)

    elif task == "Positions":
        new_data = []
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        time.sleep(2)
        worksheet.update(new_data)

    elif task == "Orders":
        new_data = []
        data = flatten_dict(data)
        header = list(data.keys())
        new_data.append(header)
        new_data.append([data.get(key, "") for key in header])
        # Update worksheet
        time.sleep(2)
        worksheet.update(new_data)

    logger.info(f"Spreadsheet updated with {task} data.")
