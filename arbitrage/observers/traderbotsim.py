import logging
import json
import os
from arbitrage.observers.traderbot import TraderBot
from arbitrage import config

class MockMarket(object):
    def __init__(self, name, fee=None, usd_balance=500., btc_balance=15.,
                 persistent=True):
        self.name = name
        self.filename = "mocks/%s/traderbot-sim-%s.json" % (config.profit_thresh, name)
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.usd_balance = usd_balance
        self.btc_balance = btc_balance
        self.fee = fee if fee else [0, 0]
        self.persistent = persistent
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def buy(self, volume, price):
        logging.info("execute buy %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.usd_balance -= price * volume
        self.btc_balance += volume - volume * (self.fee[0] + self.fee[1])
        if self.persistent:
            self.save()

    def sell(self, volume, price):
        logging.info("execute sell %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.btc_balance -= volume
        self.usd_balance += price * volume - price * volume * (self.fee[0] + self.fee[1])
        if self.persistent:
            self.save()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.usd_balance = data["usd"]
        self.btc_balance = data["btc"]

    def save(self):
        data = {'usd': self.usd_balance, 'btc': self.btc_balance}
        json.dump(data, open(self.filename, "w"))

    def balance_total(self, price):
        return self.usd_balance + self.btc_balance * price

    def get_info(self):
        pass


class TraderBotSim(TraderBot):
    def __init__(self):
        self.clients = {};

        for market_name in config.markets:
            if config.market_fees[market_name]:
                self.clients[market_name] = MockMarket(market_name,
                                                       config.market_fees[market_name],
                                                       5000, 0.5) # 0.5% fee

        self.trade_wait = 120
        self.last_trade = 0
        self.total_gain = 0

    def total_balance(self, price):
        market_balances = [i.balance_total(
            price) for i in set(self.clients.values())]
        return sum(market_balances)

    def total_usd_balance(self):
        return sum([i.usd_balance for i in set(self.clients.values())])

    def total_btc_balance(self):
        return sum([i.btc_balance for i in set(self.clients.values())])

    def execute_trade(self, volume, kask, kbid,
                      weighted_buyprice, weighted_sellprice,
                      buyprice, sellprice, perc):
        logging.info("Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))
        # self.send_telegram_message("Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))

        self.clients[kask].buy(volume, buyprice)
        self.clients[kbid].sell(volume, sellprice)

if __name__ == "__main__":
    t = TraderBotSim()
    print("Total BTC: %f" % t.total_btc_balance())
    print("Total USD: %f" % t.total_usd_balance())
