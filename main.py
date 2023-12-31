import time
import signal
from multiprocessing import Process

from app.bars import stream_bars
from app.quotes import stream_quotes
from app.orders import stream_orders
from app.positions import stream_positions
from manager import update_parameters

# Function to handle the SIGTERM signal
def sigterm_handler(signum, frame):
    print("Received SIGTERM signal. Exiting...")
    exit(0)


# Register the SIGTERM signal handler
signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == "__main__":
    bars = Process(target=stream_bars)
    quotes = Process(target=stream_quotes)
    orders = Process(target=stream_orders)
    positions = Process(target=stream_positions)

    update_parameters()

    bars.start()
    time.sleep(5)
    quotes.start()
    time.sleep(5)
    orders.start()
    time.sleep(5)
    positions.start()

    bars.join()
    quotes.join()
    orders.join()
    positions.join()
