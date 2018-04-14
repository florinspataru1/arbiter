import logging
import time
import urllib
import json
from arbitrage.observers.observer import Observer
from arbitrage.fiatconverter import FiatConverter
from arbitrage import config


class TraderBot(Observer):
    def __init__(self):
        self.clients = {
            # TODO: move that to the config file
            # "BitstampUSD": bitstampusd.PrivateBitstampUSD(),
        }
        self.fc = FiatConverter()
        self.trade_wait = 120  # in seconds
        self.last_trade = 0
        self.potential_trades = []
        self.total_gain = 0

    def begin_opportunity_finder(self, depths):
        self.potential_trades = []

    def end_opportunity_finder(self):
        if not self.potential_trades:
            return
        self.potential_trades.sort(key=lambda x: x[0])
        # logging.info("Potential trades: " + str(self.potential_trades[0]))
        # Execute only the best (more profitable)
        logging.info("Possible profit commission applied: %f; without commission: %f" %
                     (self.potential_trades[0][0], self.potential_trades[0][1]))
        logging.info("Total number of trades found: %d " % (len(self.potential_trades)))
        self.execute_trade(*self.potential_trades[0][2:])
        self.total_gain += self.potential_trades[0][0]
        logging.info("Profit total: %f " % (self.total_gain))
        message = "profit: %.2f USD with volume: %f BTC - buy at %.4f (%s) sell at %.4f (%s) ~%.2f%%" % (self.potential_trades[0][0], self.potential_trades[0][2], self.potential_trades[0][7], self.potential_trades[0][3], self.potential_trades[0][8], self.potential_trades[0][4], self.potential_trades[0][9])
        self.send_telegram_message(message)

    def get_min_tradeable_volume(self, buyprice, usd_bal, btc_bal):
        min1 = float(usd_bal) / ((1 + config.balance_margin) * buyprice)
        min2 = float(btc_bal) / (1 + config.balance_margin)
        return min(min1, min2)

    def update_balance(self):
        for kclient in self.clients:
            self.clients[kclient].get_info()

    def opportunity(self, profit, profit_total, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        if profit < config.profit_thresh or perc < config.perc_thresh:
            logging.verbose("[TraderBot] Profit or profit percentage lower than"+
                            " thresholds %f %f" % (profit, perc))
            return
        if kask not in self.clients:
            logging.verbose("[TraderBot] Can't automate this trade, client not "+
                         "available: %s" % kask)
            return
        if kbid not in self.clients:
            logging.verbose("[TraderBot] Can't automate this trade, " +
                         "client not available: %s" % kbid)
            return
        volume = min(config.max_tx_volume, volume)

        #(profit, volume, buyprice, kask, sellprice, kbid, perc)
        #(self.potential_trades[0][0], self.potential_trades[0][2], self.potential_trades[0][7], self.potential_trades[0][3], self.potential_trades[0][8], self.potential_trades[0][4], self.potential_trades[0][9])
        # Update client balance
        self.update_balance()
        max_volume = self.get_min_tradeable_volume(buyprice,
                                                   self.clients[kask].usd_balance,
                                                   self.clients[kbid].btc_balance)
        volume = min(volume, max_volume, config.max_tx_volume)
        if volume < config.min_tx_volume:
            logging.verbose("Can't automate this trade, minimum volume transaction"+
                         " not reached %f/%f" % (volume, config.min_tx_volume))
            logging.warning("Balance on %s: %f USD - Balance on %s: %f BTC"
                         % (kask, self.clients[kask].usd_balance, kbid,
                            self.clients[kbid].btc_balance))
            return
        current_time = time.time()
        if current_time - self.last_trade < self.trade_wait:
            logging.warning("[TraderBot] Can't automate this trade, last trade " +
                         "occured %.2f seconds ago" % (current_time - self.last_trade))
            return
        self.potential_trades.append([profit, profit_total, volume, kask, kbid,
                                      weighted_buyprice, weighted_sellprice,
                                      buyprice, sellprice, perc])

    def watch_balances(self):
        pass

    def execute_trade(self, volume, kask, kbid, weighted_buyprice,
                      weighted_sellprice, buyprice, sellprice, perc):
        self.last_trade = time.time()
        logging.info("Buy @%s %f BTC and sell @%s" % (kask, volume, kbid))
        self.clients[kask].buy(volume, buyprice)
        self.clients[kbid].sell(volume, sellprice)


    def send_telegram_message(self, message):
        url = "https://api.telegram.org/bot%s/sendMessage" % (config.telegram_token)
        req = urllib.request.Request(url, data=json.dumps({"chat_id": config.telegram_chat_id,"text": message}).encode('utf8'),
                                     headers={
                                         "Content-Type": "application/json",
                                         "Accept": "*/*",
                                         "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})
        try:
            res = urllib.request.urlopen(req)
        except Exception as e:
            logging.error("Can't send telegram message: %s" % (str(e)))