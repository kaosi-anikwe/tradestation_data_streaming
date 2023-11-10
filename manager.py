import os
import json
import time
import gspread
import traceback
import subprocess
from subprocess import PIPE
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

spreadsheet_id = os.getenv("SPREADSHEET_ID")
google_credentials_file = os.getenv("CREDENTIALS_FILE")
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_file, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(spreadsheet_id)


def update_parameters():
    print("Updating parameters...")
    with open("parameters.json", "r") as file:
        old_parameters = json.load(file)
    try:
        worksheet = spreadsheet.worksheet("Parameters")
        parameters = worksheet.get_all_values()
        # Extract headers and data rows
        headers = parameters[0]
        data_rows = parameters[1:]
        # Convert data to a list of dictionaries
        parameters = [dict(zip(headers, row)) for row in data_rows][0]

        if old_parameters != parameters:
            status = "Parameters updated."
            # stop
            subprocess.run(
                "shell_scripts/stop_streamer.sh", shell=True, stdout=PIPE, stderr=PIPE,
            )
            if str(parameters["SWITCH"]).lower() == "on":
                # restart
                subprocess.run(
                    "shell_scripts/start_streamer.sh",
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
            else:
                status = "Streamer is not running."
        else:
            status = (
                subprocess.run(
                    "shell_scripts/check_streamer.sh",
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode("utf-8")
                .replace("\n", "")
            )
            if "not" in status and str(parameters["SWITCH"]).lower() == "on":
                # restart
                subprocess.run(
                    "shell_scripts/start_streamer.sh",
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
            if "not" not in status and str(parameters["SWITCH"]).lower() == "off":
                subprocess.run(
                    "shell_scripts/stop_streamer.sh",
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
            status = (
                subprocess.run(
                    "shell_scripts/check_streamer.sh",
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode("utf-8")
                .replace("\n", "")
            )

        parameters.update({"STATUS": status})
        worksheet.update([list(parameters.keys()), list(parameters.values())])
        with open("parameters.json", "w") as file:
            json.dump(parameters, file)
    except:
        status = "Error reading parameters."
        print(traceback.format_exc())
        old_parameters.update({"STATUS": status})
        worksheet.update([list(old_parameters.keys()), list(old_parameters.values())])
        with open("parameters.json", "w") as file:
            json.dump(old_parameters, file)

    print("Parameters updated sucessfully!")


if __name__ == "__main__":
    while True:
        try:
            update_parameters()
        except:
            pass
        time.sleep(5)
