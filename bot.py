from poloniex import Poloniex, PoloniexError
from helpers import read_keys_from_file, calculate_avg_true_range


class Bot:
    def __init__(self):
        api_key, api_secret = read_keys_from_file()
        self.client = Poloniex(api_key, secret)
