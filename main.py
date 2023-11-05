from multiprocessing import Process

from app.bars import stream_bars
from app.quotes import stream_quotes
from app.orders import stream_orders
from app.positions import stream_positions


if __name__ == "__main__":
    bars = Process(target=stream_bars)
    quotes = Process(target=stream_quotes)
    orders = Process(target=stream_orders)
    positions = Process(target=stream_positions)

    # bars.start()
    quotes.start()
    # orders.start()
    # positions.start()

    # bars.join()
    quotes.join()
    # orders.join()
    # positions.join()
