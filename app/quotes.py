import time
import json
import requests

from . import logger
from .functions import get_access_token, update_spreadsheet


def stream_quotes():
    while True:
        try:
            url = "https://api.tradestation.com/v3/marketdata/stream/quotes/MSFT"
            headers = {"Authorization": f"Bearer {get_access_token()}"}
            # Make a GET request with streaming support
            logger.info("Making request for quotes stream.")
            response = requests.get(url, headers=headers, stream=True)

            if response.status_code == 200:
                logger.info("Now streaming quotes from response.")
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # Parse each line as JSON
                            data = json.loads(line)
                            # Check for a server error attribute (e.g., 'restart_on_attribute')
                            if "Error" in data:
                                logger.info(
                                    f"Restarting due to server response: {data}"
                                )
                                break  # Exit the loop and restart
                            # Check if stream is Heartbeat
                            if not "Heartbeat" in data:  # Quote stream
                                print(data)
                                update_spreadsheet(task="stream_quotes", data=data)

                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON: {e}")
                    else:
                        # Handle empty lines, if needed
                        pass
            else:
                logger.error(
                    f"Failed to connect to the streaming endpoint. Status code: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")

        # delay before reconnecting to the streaming endpoint
        time.sleep(5)
        logger.info("Retrying quotes stream.")
