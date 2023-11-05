import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from . import logger
from .functions import get_access_token, update_spreadsheet


def stream_positions():
    while True:
        try:
            account_ids = os.getenv("ACCOUNT_IDS")
            logger.info(account_ids)
            url = f"https://api.tradestation.com/v3/brokerage/stream/accounts/{account_ids}/positions"
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
                            if "Error" in data or "StreamStatus" in data:
                                logger.info(
                                    f"Restarting positions stream due to server response: {data}"
                                )
                                break  # Exit the loop and restart
                            # Check if stream is Heartbeat
                            if not "Heartbeat" in data:  # Positions stream
                                update_spreadsheet(task="Positions", data=data)

                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON for positions stream: {e}")
            else:
                logger.error(
                    f"Failed to connect to the positions stream endpoint. Status code: {response.status_code}. Response text: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Positions stream request error: {e}")

        # Delay before reconnecting to the streaming endpoint
        time.sleep(5)
        logger.info("Retrying positions stream.")