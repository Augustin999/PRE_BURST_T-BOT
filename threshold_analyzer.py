import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.trend import cci
from ta.momentum import rsi
from ta.volatility import BollingerBands
import requests as re
import time as tm

from scanner import futures_api, spot_api, utils


def calc_slope(x):
    """
    Compute linear regressions on a rolling window and store the calculated slope.
    """
    slopes = np.polyfit(range(len(x)), x, 1)[0]
    return slopes


def load_latest_futures_ohlc(pair):
    """
    Pull future OHLCV data from the Binance API.
    """
    next_timestamp = utils.load_pickle(utils.data_path)['next timestamp']
    limit = 1500 # 3*utils.CCI_PERIOD
    ohlc = futures_api.get_contract_klines(pair, utils.TIMEFRAME, contractType='PERPETUAL', limit=limit)
    ohlc = pd.DataFrame(ohlc, columns=utils.OHLC_COLUMNS)
    ohlc = ohlc[ohlc['open_time'] < 1000*next_timestamp.timestamp()]
    ohlc['open_time'] = pd.to_datetime(ohlc['open_time'], unit='ms')
    return ohlc


def compute_technical_indicators(ohlc):
    """
    Calculate some technical indicators that will be usefull for examining signals.
    *** THIS FUNCTION MUST BE EDITED ACCORDING TO THE TARGETTED SIGNALS ***
    """
    BB = BollingerBands(ohlc['close_price'], utils.BB_PERIOD, utils.BB_MULTIPLIER)
    ohlc['BBh'] = BB.bollinger_hband()
    ohlc['BBl'] = BB.bollinger_lband()
    ohlc['cci'] = cci(high=ohlc['high_price'], low=ohlc['low_price'], close=ohlc['close_price'], window=utils.CCI_PERIOD)
    ohlc['rsi'] = rsi(close=ohlc['close_price'], window=utils.RSI_PERIOD)
    ohlc['BBh_slope'] = ohlc['BBh'].rolling(utils.N_DIFF, min_periods=2).apply(calc_slope)
    ohlc['BBl_slope'] = ohlc['BBl'].rolling(utils.N_DIFF, min_periods=2).apply(calc_slope)
    ohlc['BB_slopes_diff'] = ohlc['BBh_slope'] + ohlc['BBl_slope']
    ohlc['BB_span'] = (ohlc['BBh'] - ohlc['BBl']) / ohlc['close_price']
    ohlc['pre_burst'] = np.where(ohlc['BB_span'] <= BB_SPAN_THRESHOLD, True, False)
    return ohlc


def create_opportunity_plot(ohlc, pair):
    """
    Create a chart containing useful information about the current state of the market.
    *** THIS FUNCTION MUST BE EDITED ACCORDING TO THE TARGETTED SIGNALS ***
    """
    fig = plt.figure(figsize=(12, 6))
    # Plot OHLC prices + Bollinger Bands + PreBurst Signals
    ax1 = fig.add_subplot(211)
    ax1.plot(ohlc['close_time'], ohlc['BBh'], color='red', linewidth=0.5)
    ax1.plot(ohlc['close_time'], ohlc['BBl'], color='red', linewidth=0.5)
    ax1.fill_between(ohlc['close_time'], y1=ohlc['BBl'], y2=ohlc['BBh'], color='pink')
    ax1.scatter(ohlc['close_time'], ohlc['high_price'], marker='.', color='darkblue', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['low_price'], marker='.', color='red', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['open_price'], marker='.', color='orange', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['close_price'], marker='.', color='cyan', s=10)
    ax1.scatter(ohlc[ohlc['pre_burst'] == True]['close_time'], ohlc[ohlc['pre_burst'] == True]['close_price'], marker='*', color='yellow', s=30)
    ax1.set_ylabel('OHLC & BB', fontsize=18)
    ax1.set_title(pair.upper(), fontsize=20)
    # Plot the Bollinger Bands span
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.plot(ohlc['close_time'], ohlc['BB_span'], color='red', linewidth=0.8)
    ax2.plot(ohlc['close_time'], [0]*len(ohlc['close_time']), color='black', linewidth=0.8)
    ax2.fill_between(x=ohlc['close_time'], y1=[0]*len(ohlc['close_time']), y2=ohlc['BB_span'], color='pink')
    ax2.set_ylabel('BB span', fontsize=18)
    # Save the figure in the appropriate location
    plt.tight_layout()
    # img_path = utils.images_path / f'{pair.upper()}_opp.png'
    # plt.savefig(img_path)
    plt.show()
    return 



# BTCUSDT: 0.035
# ETHUSDT: 0.10
# ADAUSDT: 0.08
# LINKUSDT: 0.08

if __name__ == '__main__':
    # %matplotlib widget
    pair = 'ETHUSDT'
    BB_SPAN_THRESHOLD = 0.1
    ohlc = load_latest_futures_ohlc(pair)
    ohlc = compute_technical_indicators(ohlc)
    create_opportunity_plot(ohlc, pair)