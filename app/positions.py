import os
import time
import json
import requests
import traceback
from dotenv import load_dotenv

load_dotenv()

from . import logger
from .functions import get_access_token, update_spreadsheet, get_parameters


def stream_positions():
    while True:
        try:
            account_id = get_parameters()["ACCOUNT_ID"]
            url = f"https://api.tradestation.com/v3/brokerage/stream/accounts/{account_id}/positions"
            headers = {"Authorization": f"Bearer {get_access_token()}"}
            # Make a GET request with streaming support
            logger.info("Making request for positions stream.")
            response = requests.get(url, headers=headers, stream=True)

            if response.status_code == 200:
                logger.info("Now streaming positions from response.")
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # Parse each line as JSON
                            data = json.loads(line)
                            # Check for a server error
                            if "Error" in data:
                                logger.info(
                                    f"Restarting positions stream due to server response: {data}"
                                )
                                break  # Exit the loop and restart
                            # Check stream status
                            if "StreamStatus" in data:
                                if data["StreamStatus"] == "GoAway":
                                    logger.info(
                                        f"Restarting positions stream due to StreamStatus: {data}"
                                    )
                                    break
                            # Check if stream is Heartbeat
                            if (
                                not "Heartbeat" in data and "StreamStatus" not in data
                            ):  # Positions stream
                                try:
                                    update_spreadsheet(task="Positions", data=data)
                                except Exception as e:
                                    logger.error(
                                        f"Error updating Positions spreadsheet"
                                    )
                                    logger.error(e)
                                    break

                        except Exception as e:
                            logger.error(e)
            else:
                logger.error(
                    f"Failed to connect to the positions stream endpoint. Status code: {response.status_code}. Response text: {response.text}"
                )
        except Exception as e:
            logger.error(e)

        # Delay before reconnecting to the streaming endpoint
        time.sleep(5)
        logger.info("Retrying positions stream.")
