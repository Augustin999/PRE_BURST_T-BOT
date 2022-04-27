# PreBurst Signals Telegram Bot
#
# Antoine Beretto
# GitHub: @augustin999
#
# April 2021

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
    limit = 3*utils.CCI_PERIOD
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
    BB = BollingerBands(ohlc['close_price'], utils.BB_PERIOD, utils.BB_PERIOD)
    ohlc['BBh'] = BB.bollinger_hband()
    ohlc['BBl'] = BB.bollinger_lband()
    ohlc['cci'] = cci(high=ohlc['high_price'], low=ohlc['low_price'], close=ohlc['close_price'], window=utils.CCI_PERIOD)
    ohlc['rsi'] = rsi(close=ohlc['close_price'], window=utils.RSI_PERIOD)
    ohlc['BBh_slope'] = ohlc['BBh'].rolling(utils.N_DIFF, min_periods=2).apply(calc_slope)
    ohlc['BBl_slope'] = ohlc['BBl'].rolling(utils.N_DIFF, min_periods=2).apply(calc_slope)
    ohlc['BB_slopes_diff'] = ohlc['BBh_slope'] + ohlc['BBl_slope']
    ohlc['BB_span'] = (ohlc['BBh'] - ohlc['BBl']) / ohlc['close_price']
    ohlc['pre_burst'] = np.where(ohlc['BB_span'] <= utils.BB_SPAN_THRESHOLD, True, False)
    return ohlc


def create_opportunity_plot(ohlc, pair):
    """
    Create a chart containing useful information about the current state of the market.
    *** THIS FUNCTION MUST BE EDITED ACCORDING TO THE TARGETTED SIGNALS ***
    """
    fig = plt.figure(figsize=(15, 8))
    # Plot OHLC prices + Bollinger Bands + PreBurst Signals
    ax1 = fig.add_subplot(411)
    ax1.plot(ohlc['close_time'], ohlc['BBh'], color='red', linewidth=0.5)
    ax1.plot(ohlc['close_time'], ohlc['BBl'], color='red', linewidth=0.5)
    ax1.fill_between(ohlc['close_time'], y1=ohlc['BBl'], y2=ohlc['BBh'], color='pink')
    ax1.scatter(ohlc['close_time'], ohlc['high_price'], marker='.', color='darkblue', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['low_price'], marker='.', color='red', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['open_price'], marker='.', color='orange', s=10)
    ax1.scatter(ohlc['close_time'], ohlc['close_price'], marker='.', color='cyan', s=10)
    ax1.scatter(ohlc[ohlc['pre_burst'] == True]['close_time'], ohlc[ohlc['pre_burst'] == True]['close_price'], marker='*', color='red', s=30)
    ax1.set_ylabel('OHLC & BB', fontsize=18)
    ax1.set_title(pair.upper(), fontsize=20)
    # Plot the Bollinger Bands slopes difference
    ax2 = fig.add_subplot(412, sharex=ax1)
    ax2.plot(ohlc['close_time'], ohlc['BB_slopes_diff'], color='red', linewidth=0.8)
    ax2.plot(ohlc['close_time'], [0]*len(ohlc['close_time']), color='black', linewidth=0.8)
    ax2.fill_between(x=ohlc['close_time'], y1=[0]*len(ohlc['close_time']), y2=ohlc['BB_slopes_diff'], color='pink')
    ax2.set_ylabel('BB slopes diff', fontsize=18)
    # Plot the CCI
    ax3 = fig.add_subplot(413, sharex=ax1)
    ax3.plot(ohlc['close_time'], ohlc['cci'], color='darkblue', linewidth=0.8)
    ax3.plot(ohlc['close_time'], [-100] * len(ohlc['close_time']), color='red', linewidth=0.8)
    ax3.plot(ohlc['close_time'], [100] * len(ohlc['close_time']), color='red', linewidth=0.8)
    ax3.fill_between(ohlc['close_time'], y1=[-100] * len(ohlc['close_time']), y2=[100] * len(ohlc['close_time']), color='lightblue')
    ax3.set_ylabel('CCI', fontsize=18)
    # Plot the RSI
    ax4 = fig.add_subplot(414, sharex=ax1)
    ax4.plot(ohlc['close_time'], ohlc['rsi'], color='darkblue', linewidth=0.8)
    ax4.plot(ohlc['close_time'], [30]*len(ohlc['close_time']), color='red', linewidth=0.8)
    ax4.plot(ohlc['close_time'], [70]*len(ohlc['close_time']), color='red', linewidth=0.8)
    ax4.fill_between(x=ohlc['close_time'], y1=[30]*len(ohlc['close_time']), y2=[70]*len(ohlc['close_time']), color='lightblue')
    ax4.set_ylabel('RSI', fontsize=18)
    ax4.set_xlabel('Close time', fontsize=18)
    # Save the figure in the appropriate location
    plt.tight_layout()
    img_path = utils.images_path / f'{pair.upper()}_opp.png'
    plt.savefig(img_path)
    plt.close('all')
    return 


def update_opportunity(pair, opp):
    ohlc = load_latest_futures_ohlc(pair)
    cci_opp = opp['cci']
    latest_cci = ohlc['cci'].iloc[-1]
    if cci_opp < -100 and latest_cci > -100:
        delete = True
    elif cci_opp > 100 and latest_cci < 100:
        delete = True
    else:
        delete = False
    return delete


def scan_market(pair):
    """ Look for trading opportunities for one single pair """
    # Get the latest OHLCV values with useful indicators
    ohlc = load_latest_futures_ohlc(pair)
    ohlc = compute_technical_indicators(ohlc)
    pre_burst_signal = ohlc['pre_burst'].iloc[-1]
    # If there is no signal, there is nothing else to do
    if not pre_burst_signal:
        return None
    # Otherwise, we create and store a plot of the market's state
    create_opportunity_plot(ohlc, pair)
    # Finally, we return the values of the opportunity
    price = futures_api.get_price(pair)
    opportunity = {
        'pair': pair.upper(),
        'time': pd.Timestamp(int(tm.time()), unit='s'),
        'price': price,
        'cci': round(ohlc['cci'].iloc[-1], 2),
        'rsi': round(ohlc['rsi'].iloc[-1], 2)
    }
    return opportunity