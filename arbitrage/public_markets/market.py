import time
import urllib.request
import urllib.error
import urllib.parse
import logging
import json
from arbitrage import config
from arbitrage.fiatconverter import FiatConverter
from arbitrage.utils import log_exception

class Market(object):
    def __init__(self, currency, cryptowatch_code=None):
        self.name = self.__class__.__name__
        self.currency = currency
        self.cryptowatch_code = cryptowatch_code
        self.cryptowatch_price = 0
        self.depth_updated = 0
        self.update_rate = 60
        self.fc = FiatConverter()
        self.fc.update()

    def get_cryptowatch_price(self):
        if not self.cryptowatch_code:
            return

        url = ('https://api.cryptowat.ch/markets/' +
            self.name.lower().replace('usd', '').replace('eur', '') +
            '/' + self.cryptowatch_code + '/price')

        res = urllib.request.urlopen(url)
        jsonstr = res.read().decode('utf8')
        try:
            price = json.loads(jsonstr)
        except Exception:
            logging.error("Cryptowatch %s - Can't parse json: %s" % (self.name, jsonstr))
        self.cryptowatch_price = self.fc.convert(price["result"]["price"], self.currency , "USD")

    def double_ckeck_price(self, price, direction, allowed_percent=None):
        if self.cryptowatch_price == 0:
            self.get_cryptowatch_price()

        allowed_percent = allowed_percent if allowed_percent else 10

        if abs(price - self.cryptowatch_price) > self.cryptowatch_price * allowed_percent / 100:
            logging.error("Big diff. @%s depth price(%s) vs Cryptowatch price %f / %f" %
                          (self.name, direction, price, self.cryptowatch_price))
            return False

        return True

    def get_depth(self):
        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            self.ask_update_depth()
        timediff = time.time() - self.depth_updated
        if timediff > config.market_expiration_time:
            logging.warning('Market: %s order book is expired' % self.name)
            self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
                {'price': 0, 'amount': 0}]}
        return self.depth

    def convert_to_usd(self):
        if self.currency == "USD":
            return
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                # self.double_ckeck_price(order["price"], direction, order)
                # we don't do it here any more
                order["price"] = self.fc.convert(order["price"], self.currency, "USD")

    # there are some prices inside the market depth that are ment to de destabilize the market
    # clear them out
    def sort_out_market_crush_prices(self):
        new_depth = {'asks': [], 'bids': []}
        for direction in ("asks", "bids"):
            for order in self.depth[direction]:
                if self.double_ckeck_price(order["price"], direction, 30):
                    new_depth[direction].append(order)

        if len(new_depth["ask"]) != len(self.depth["ask"]) or len(new_depth["bids"]) != len(self.depth["bids"]):
            logging.warning('Market: %s removed some market crush crush items' % self.name)

        self.depth = new_depth

    def ask_update_depth(self):
        try:
            self.update_depth()
            self.convert_to_usd()
            self.get_cryptowatch_price()
            self.depth_updated = time.time()
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logging.error("HTTPError, can't update market: %s" % self.name)
            log_exception(logging.DEBUG)
        except Exception as e:
            logging.error("Can't update market: %s - %s" % (self.name, str(e)))
            log_exception(logging.DEBUG)

    def get_ticker(self):
        depth = self.get_depth()
        res = {'ask': 0, 'bid': 0}
        if len(depth['asks']) > 0 and len(depth["bids"]) > 0:
            res = {'ask': depth['asks'][0],
                   'bid': depth['bids'][0]}
        return res

    ## Abstract methods
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass
