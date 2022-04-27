# PreBurst Signals Telegram Bot
#
# Antoine Beretto
# GitHub: @augustin999
#
# April 2021

import telegram
from telegram.ext.updater import Updater
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Handler, CallbackContext, CallbackQueryHandler, ConversationHandler, callbackcontext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
import threading
import os
import pandas as pd
import time as tm

from scanner import models, utils, scanner, futures_api, spot_api



def display_universe(update: Update, context: CallbackContext):
    """ Tell user all the pairs in the futures universe """
    msg = "List of pairs in universe:\n"
    data = utils.load_pickle(utils.data_path)
    universe = data['universe']
    for pair in universe:
        msg += f'\n\t{pair}'
    update.message.reply_text(msg)
    return

# --------------------------------------------------
#          SCHEDULED OPPORTUNITIES RESEARCH
# --------------------------------------------------

def periodic_1h_process(update: Update, context: CallbackContext):
    # Wait for next timestamp
    next_timestamp = utils.load_pickle(utils.data_path)['next timestamp']
    t = pd.Timestamp(futures_api.get_server_time(), unit='ms')
    while t < next_timestamp + pd.Timedelta('1M'):
        if t < next_timestamp - pd.Timedelta('1M'):
            # print('Sleep for 60s')
            tm.sleep(10)
        elif t < next_timestamp:
            # print('Sleep for 5s')
            tm.sleep(5)
        else:
            # Search for opportunities on every markets
            opportunity_scan(update, context)
            # Update next timestamp
            print('Scan done')
            data = utils.load_pickle(utils.data_path)
            data['next timestamp'] = data['next timestamp'] + pd.Timedelta(utils.TIMEFRAME)
            utils.dump_pickle(data, utils.data_path)
        next_timestamp = utils.load_pickle(utils.data_path)['next timestamp']
        t = pd.Timestamp(futures_api.get_server_time(), unit='ms')
    return


def initiate_opportunity_scans(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    data = utils.load_pickle(utils.data_path)
    if data['nThreads'] == 0:
        data['nThreads'] = 1
        utils.dump_pickle(data, utils.data_path)
        msg = 'Starting scans loop'
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)
        periodic_1h_thread = threading.Thread(target=periodic_1h_process, args=[update, context])
        periodic_1h_thread.start()
    else:
        msg = 'Scans loop already initiated'
        bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)
    return


def opportunity_scan(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    # Clear previous opportunities
    data = utils.load_pickle(utils.data_path)
    if 'opportunities' in data.keys():
        key_pairs = list(data['opportunities'].keys())
        for pair in key_pairs:
            img_path = utils.images_path / f'{pair.upper()}_opp.png'
            if os.path.exists(img_path):
                os.remove(img_path)
            del data['opportunities'][pair]
    # Now, scan and display the new opportunities
    opportunities = dict()
    for pair in utils.UNIVERSE:
        opp = scanner.scan_market(pair)
        if opp != None:
            opportunities[pair] = opp
            path = utils.images_path / f'{pair}_opp.png'
            opp_description = f'<b>New trading opportunity: {pair.upper()}</b>'
            opp_description += f"\n time: {opp['time']}"
            opp_description += f"\n price: {opp['price']}"
            opp_description += f"\n CCI: {opp['cci']}"
            opp_description += f"\n RSI: {opp['rsi']}"
            
            bot.send_message(chat_id=chat_id, text=opp_description, parse_mode=telegram.ParseMode.HTML)
            bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))
    data['opportunities'] = opportunities
    return

# --------------------------------------------------
#      END OF SCHEDULED OPPORTUNITIES RESEARCH
# --------------------------------------------------

# --------------------------------------------------
#               T-BOT INITIALISATION
# --------------------------------------------------

def help(update: Update, context: CallbackContext):
    """ Returns all commands available in the bot. """
    msg = "<b>General commands:</b>\n"
    msg += "\n\t<b>\\help</b> - return list of commands"
    msg += "\n\t<b>\\display_universe</b> - show listed pairs on which to look for trading opportunities"
    msg += "\n\t<b>\init_scans</b> - initiate loop to scan markets for opportunities periodically"

    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=msg, parse_mode=telegram.ParseMode.HTML)
    return


def initiate_account():
    """
    If not already existing, create a data file and two Account instances, one for 
    Paper Trading, the other for Real Trading.
    """
    # Set up next_timestamp
    timedelta = pd.Timedelta(utils.TIMEFRAME)
    t = pd.Timestamp(int(tm.time()), unit='s')
    divider = int(timedelta.to_timedelta64()/10**9/60)

    next_timestamp = pd.Timestamp(
        year=t.year,
        month=t.month,
        day=t.day,
        hour=t.hour,
        minute=divider*(t.minute//divider)
    ) + timedelta
    data = {
        'next timestamp': next_timestamp,
        'universe': utils.UNIVERSE,
        'nThreads': 0,
        'opportunities': dict()
    }
    utils.dump_pickle(data, utils.data_path)
    return

if __name__ == '__main__':
    telegram_token = utils.read_file(path=utils.telegram_token_path)
    initiate_account()
    updater = Updater(telegram_token)
    bot = telegram.Bot(telegram_token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('init_scans', initiate_opportunity_scans))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('display_universe', display_universe))
    updater.start_polling()
    updater.idle()