from poloniex import Poloniex, PoloniexError
from helpers import read_keys_from_file, calculate_avg_true_range, dump_json_to_file
from constants import *
import time


class Bot:
    def __init__(self):
        api_key, api_secret = read_keys_from_file()
        self.client = Poloniex(api_key, api_secret)
        self.stop_losses = {}
        self.stop_distances = {}
        self.ticks = {}
        self.stamps = {}
        self.atr = {}

    def log_finished_trade(self, pair, position, close):
        position['stamp'] = self.stamps[pair]
        position['pair'] = pair
        position['atr'] = self.atr[pair]
        entry = float(position['basePrice'])
        exit = float(close['resultingTrades'][pair][0]['rate'])
        pl, pl_percent = (0, 0)
        if position['type'] == 'short':
            pl = (entry - exit) * abs(float(position['amount']))
            pl_percent = ((entry - exit) / exit) * 100
        if position['type'] == 'long':
            pl = (exit - entry) * abs(float(position['amount']))
            pl_percent = ((exit - entry) / exit) * 100
        data = {
            "position": position,
            "closing_trades": close['resultingTrades'][pair],
            "stop_losses": self.stop_losses[pair],
            "tickers": self.ticks[pair],
            "profit_loss": [pl, pl_percent]
        }
        path = TRADES_FOLDER_PATH + '/%s-%s-%s.json' % (pair, position['type'], str(int(position['stamp'])))
        dump_json_to_file(path, data)
        del self.stop_distances[pair]
        del self.stop_losses[pair]
        del self.ticks[pair]
        del self.atr[pair]
        del self.stamps[pair]

    def get_tick(self, pair, tickers):
        tick = tickers[pair]
        bid = float(tick['highestBid'])
        ask = float(tick['lowestAsk'])
        if pair not in self.ticks:
            self.ticks[pair] = []
        self.ticks[pair].append({"bid": bid, "ask": ask})
        return bid, ask

    def get_chart(self, pair, start, end):
        while True:
            try:
                chart = self.client.returnChartData(pair, CANDLE_PERIOD, start, end)
                return chart
            except PoloniexError as e:
                print('PoloniexError when getting chart: ', e)
                time.sleep(TICK_RATE / 2)

    def set_stop_loss(self, pair, base_price, direction):
        start = time.time() - (CANDLE_PERIOD * ATR_PERIOD)
        end = time.time()
        candle_chart = self.get_chart(pair, start, end)
        atr = calculate_avg_true_range(candle_chart)
        distance = atr * STOP_LOSS
        if direction == 'short':
            stop_loss = base_price + distance
        else:
            stop_loss = base_price - distance
        self.stop_losses[pair] = [stop_loss]
        self.stop_distances[pair] = distance
        self.stamps[pair] = end
        self.atr[pair] = atr

    def get_open_positions(self):
        open_positions = {}
        while True:
            try:
                position_data = self.client.getMarginPosition('all')
                for p in position_data:
                    if position_data[p]['type'] not in ['short', 'long']:
                        continue
                    open_positions[p] = position_data[p]
                return open_positions
            except PoloniexError as e:
                print('PoloniexError when getting positions: ', e)
                time.sleep(TICK_RATE / 2)

    def fill_chart_data(self, pair):
        # appends previous stop loss value if unchanged, for smooth chart
        if pair in self.stop_losses and len(self.ticks[pair]) > len(self.stop_losses[pair]):
            last = self.stop_losses[pair][-1]
            self.stop_losses[pair].append(last)

    def run(self):
        while True:
            try:
                open_positions = self.get_open_positions()
                if not open_positions:
                    time.sleep(TICK_RATE / 2)
                    continue
                tickers = self.client.returnTicker()
                for pair in open_positions:
                    position = open_positions[pair]
                    direction = position['type']
                    quote, base = pair.split('_')
                    base_price = float(position['basePrice'])
                    amount = float(position['amount'])
                    bid, ask = self.get_tick(pair, tickers)
                    pl, pl_percent = (0, 0)

                    if pair not in self.stop_distances:
                        self.set_stop_loss(pair, base_price, direction)

                    print('[%s %s]' % (pair, direction.upper()))
                    print('-- Base price    : %.8f %s' % (base_price, quote))

                    if direction == 'short':
                        print('-- Current price : %.8f %s' % (ask, quote))
                        pl = (base_price - ask) * abs(amount)
                        pl_percent = (base_price - ask) / ask

                        if ask < base_price:
                            accelerate = 1 - (abs(pl_percent) * ACCELERATE)
                            print('-- Position in profit, multiplying stop distance by %.4f' % accelerate)
                            self.stop_distances[pair] *= accelerate
                            new_stop_loss = ask + self.stop_distances[pair]
                            if new_stop_loss < self.stop_losses[pair][-1]:
                                self.stop_losses[pair].append(new_stop_loss)

                        stop_loss = self.stop_losses[pair][-1]
                        distance = self.stop_distances[pair]

                        if ask < (stop_loss - distance):
                            new_stop_loss = ask + distance
                            self.stop_losses[pair].append(new_stop_loss)

                        self.fill_chart_data(pair)
                        print('-- stop loss     : %.8f %s (distance: %.8f %s)' % (self.stop_losses[pair][-1], quote,
                                                                                  self.stop_distances[pair], quote))

                        if ask > self.stop_losses[pair][-1]:
                            # stop loss reached
                            close_position = self.client.closeMarginPosition(pair)
                            self.log_finished_trade(pair, position, close_position)

                    if direction == 'long':
                        print('-- Current price : %.8f %s' % (bid, quote))
                        pl = (bid - base_price) * abs(amount)
                        pl_percent = (bid - base_price) / bid

                        if bid > base_price:
                            accelerate = 1 - (abs(pl_percent) * ACCELERATE)
                            print('-- Position in profit, multiplying stop distance by %.4f' % accelerate)
                            self.stop_distances[pair] *= accelerate
                            new_stop_loss = bid - self.stop_distances[pair]
                            if new_stop_loss > self.stop_losses[pair][-1]:
                                self.stop_losses[pair].append(new_stop_loss)

                        if bid > (self.stop_losses[pair][-1] + self.stop_distances[pair]):
                            new_stop_loss = bid - self.stop_distances[pair]
                            self.stop_losses[pair].append(new_stop_loss)

                        self.fill_chart_data(pair)
                        print('-- stop loss     : %.8f %s (distance: %.8f %s)' % (self.stop_losses[pair][-1], quote,
                                                                                  self.stop_distances[pair], quote))

                        if bid < self.stop_losses[pair][-1]:
                            # stop loss reached
                            close_position = self.client.closeMarginPosition(pair)
                            self.log_finished_trade(pair, position, close_position)

                    print('-- P/L: %.8f %s (%.2f %%)' % (pl, quote, pl_percent * 100))
                time.sleep(TICK_RATE)
            except KeyboardInterrupt:
                print('manual interrupt')
                return
