import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from . import logger
from .functions import get_access_token, update_spreadsheet


def stream_bars():
    while True:
        try:
            symbol = os.getenv("BAR_SYMBOL")
            url = (
                f"https://api.tradestation.com/v3/marketdata/stream/barcharts/{symbol}"
            )
            headers = {"Authorization": f"Bearer {get_access_token()}"}
            # Make a GET request with streaming support
            logger.info("Making request for bars stream.")
            response = requests.get(url, headers=headers, stream=True)

            if response.status_code == 200:
                logger.info("Now streaming bars from response.")
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # Parse each line as JSON
                            data = json.loads(line)
                            # Check for a server error
                            if "Error" in data:
                                logger.info(
                                    f"Restarting bars stream due to server response: {data}"
                                )
                                break  # Exit the loop and restart
                            # Check if stream is Heartbeat
                            if not "Heartbeat" in data:  # Bars stream
                                update_spreadsheet(task="Bars", data=data)

                        except Exception as e:
                            logger.error(f"Error parsing JSON for bars stream: {e}")
            else:
                logger.error(
                    f"Failed to connect to the bars stream endpoint. Status code: {response.status_code}. Response text: {response.text}"
                )
        except Exception as e:
            logger.error(f"Bars stream request error: {e}")

        # Delay before reconnecting to the streaming endpoint
        time.sleep(5)
        logger.info("Retrying bars stream.")
