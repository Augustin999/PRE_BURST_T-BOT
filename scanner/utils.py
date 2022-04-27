# PreBurst Signals Telegram Bot
#
# Antoine Beretto
# GitHub: @augustin999
#
# April 2021

import os
import pickle
from pathlib import Path

UNIVERSE = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'LINKUSDT']

# OPPORTUNITY SCANS SETTINGS
TIMEFRAME = '1h'
BB_PERIOD = 20
BB_MULTIPLIER = 2
CCI_PERIOD = 160
RSI_PERIOD = 20
N_DIFF = 3
BB_SPAN_THRESHOLD = 0.025

# GENERAL SETTINGS

OHLC_COLUMNS = [
    'open_time',
    'open_price',
    'high_price',
    'low_price',
    'close_price',
    'volume',
    'close_time',
    'quote_volume',
    'number_of_trades',
    'taker_buy_volume',
    'taker_buy_quote_volume',
]

root = Path(os.getcwd())

keys_path = root / 'keys'
public_key_path = keys_path / 'api_public_key'
private_key_path = keys_path / 'api_private_key'
telegram_token_path = keys_path / 'telegram_token'

files_path = root / 'files'
data_path = files_path / 'data.pickle'
images_path = files_path / 'images'


def read_file(path: Path):
    """Read text file (eg: api keys)"""
    with open(path, 'r') as _file:
        return _file.read().strip()


def load_pickle(path: Path):
    """Load a pickle object from file"""
    file = pickle.load(open(path, 'rb'))
    return file


def dump_pickle(obj, path: Path):
    """Save a pickle object to file"""
    pickle.dump(obj, open(path, 'wb'))
    return