markets = [
    # "BitFlyerEUR",
    # "BitFlyerUSD",
    "BitfinexEUR",
    "BitfinexUSD",
    "BinanceUSD",
    "PoloniexUSD",
    "BitstampEUR",
    "BitstampUSD",
    # "CEXEUR",
    # "CEXUSD",
    # "GDAXEUR",
    # "GDAXUSD",
    # "GeminiUSD",
    "KrakenEUR",
    "KrakenUSD",
    # "PaymiumEUR"
]

market_fees = {
    "BitfinexEUR": [0.100/100, 0.200/100],
    "BitfinexUSD": [0.100/100, 0.200/100],
    "BinanceUSD": [0.1/100, 0.1/100],
    "PoloniexUSD": [0.15/100, 0.25/100],
    "BitstampEUR": [0.25/100, 0],
    "BitstampUSD": [0.25/100, 0],
    "GeminiUSD": [0.25/100, 0.25/100],
    "KrakenEUR": [0.16/100, 0.26/100],
    "KrakenUSD": [0.16/100, 0.26/100],
}

# observers if any
# ["Logger", "DetailedLogger", "TraderBot", "TraderBotSim", "HistoryDumper", "Emailer"]
# observers = ["Logger"]
observers = ["TraderBotSim", "DetailedLogger"]

market_expiration_time = 120  # in seconds: 2 minutes

refresh_rate = 30

#### Trader Bot Config
# Access to Private APIs

paymium_username = "FIXME"
paymium_password = "FIXME"
paymium_address = "FIXME"  # to deposit btc from markets / wallets

bitstamp_username = "FIXME"
bitstamp_password = "FIXME"

# SafeGuards
max_tx_volume = 0.2  # in BTC
min_tx_volume = 0.001  # in BTC
balance_margin = 0.1  # 10%
profit_thresh = 1  # in EUR
perc_thresh = 0.1  # in %

#### Emailer Observer Config
smtp_host = 'FIXME'
smtp_login = 'FIXME'
smtp_passwd = 'FIXME'
smtp_from = 'FIXME'
smtp_to = 'FIXME'

#### XMPP Observer
xmpp_jid = "FROM@jabber.org"
xmpp_password = "FIXME"
xmpp_to = "TO@jabber.org"

######Telegram
telegram_chat_id = -313468493
telegram_token = "526734068:AAExesOnBGWdh-O6kxkOhbpfOjqllrilR6k"
