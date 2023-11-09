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
    try:
        print("Updating parameters...")
        worksheet = spreadsheet.worksheet("Parameters")
        parameters = worksheet.get_all_records()[0]
        with open("parameters.json", "w") as file:
            json.dump(parameters, file)

        status = (
            subprocess.run(
                "shell_scripts/check_streamer.sh", shell=True, stdout=PIPE, stderr=PIPE
            )
            .stdout.decode("utf-8")
            .replace("\n", "")
        )

        if str(parameters.get("SWITCH", "")).lower() == "off":
            # stop streamer
            if not "not" in status:
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
        elif str(parameters.get("SWITCH", "")).lower() == "on":
            # start streamer
            if "not" in status:
                subprocess.run(
                    "shell_scripts/start_streamer.sh",
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

        print("Parameters updated sucessfully!")
    except:
        print("Error updating parameters:")
        print(traceback.format_exc())


if __name__ == "__main__":
    while True:
        update_parameters()
        time.sleep(10)
