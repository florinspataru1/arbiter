from arbitrage.public_markets._poloniex import Poloniex

class PoloniexUSD(Poloniex):
    def __init__(self):
        super().__init__("USD", "USDT_BTC", "btcusdt")
