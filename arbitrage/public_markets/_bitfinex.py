import urllib.request
import urllib.error
import urllib.parse
import json
import logging
from arbitrage.public_markets.market import Market


class Bitfinex(Market):
    def __init__(self, currency, code, cryptowatch_code=None):
        super().__init__(currency, cryptowatch_code if cryptowatch_code != None else code.lower())
        self.code = code
        self.update_rate = 20

    def update_depth(self):
        url = 'https://api.bitfinex.com/v1/book/' + self.code
        req = urllib.request.Request(url, None,
                                     headers={
                                         "Content-Type": "application/json",
                                         "Accept": "*/*",
                                         "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})

        # res = urllib.request.urlopen(
        #     'https://api.bitfinex.com/v1/book/' + self.code)
        # jsonstr = res.read().decode('utf8')
        try:
            res = urllib.request.urlopen(req)
            depth = json.loads(res.read().decode('utf8'))
            self.depth = self.format_depth(depth)
        except Exception as e:
            logging.error("%s - Can't parse json: %s" % (self.name, str(e)))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['price']),
                      'amount': float(i['amount'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}
