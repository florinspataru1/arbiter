import urllib.request
import urllib.error
import urllib.parse
import json
import logging
from arbitrage.public_markets.market import Market


class Poloniex(Market):
    def __init__(self, currency, code, cryptowatch_code=None):
        super().__init__(currency, cryptowatch_code if cryptowatch_code != None else code.lower())
        self.code = code
        self.update_rate = 20

    def update_depth(self):
        res = urllib.request.urlopen(
            'https://poloniex.com/public?command=returnOrderBook&depth=10&currencyPair=' + self.code)
        jsonstr = res.read().decode('utf8')
        try:
            depth = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        self.depth = self.format_depth(depth)

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]),
                      'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}
