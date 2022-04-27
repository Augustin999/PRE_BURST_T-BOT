# PRE BURST SIGNALS TELEGRAM BOT

Up to this day I had several trading idea that I did not manage to fully automate. They still require a kind of human educated eye to decide exactly and with a high win rate when to open a position and in which direction. Therefore, I decided to create a tool halfway between a fully automated trading bot and manual trading: a bot that send alerts when some trading opportunities may be active. Here is the what I coded. The strategy that comes with the tool is just an example. You can copy this project and set up your own strategy if you want. 

## Description of the idea

I noted that most trading strategies usually give interesting trading signals but the false one are always destroying the overall performance. It is very difficult to automatically sort bad signals from good ones. The fundamental reason behind that is that technical indicators are not predictive. They just translate a portion of the current or past market state. In the end, identifying good signals is possible but only manually, by observing the evolution of the market and most all, its dynamic. For example, I saw that when Bollinger Bands tends to get clother and their width to get thinner and thinner, the market often pumps or dumps right after that. But knowing in which direction the move will happen is a lot more difficult. I usually manage to guess it correctly by observing how the price is evolving (does it start to move more quickly on a minutely chart ? In which direction ?), and what the combination of the RSI and CCI tells me about the strength of the price level or trend. I personnaly like these three indicators because they all measure something different : volatility for the Bollinger Bands, momentum for the RSI, trend for the CCI. Beyond that, one must train his eye to kind of *feel* the market. That is why my telegram bot is not a magic tool in the end. It only solve one problem : not spending days in front of charts to wait for an opportunity to appear. This bot will send you a message when something may be happening. 

## How to launch the bot

To make this functionnal you need to have a functionnal telegram bot (create it on the BotFather channel) with the corresponding token. Save this token in the *keys* directory. Then this project uses the Binance API to pull OHLCV data periodically. You will need a Binance account and the private and public keys of an API. Put these keys in the *keys* directory. Your *keys* directory should look like this :

keys/
    telegram_token
    api_public_key
    api_private_key

Now you can run the bot locally by executing the tBot.py file in a Python instance (terminal or notebook). As the bot is continuesly listening to the telegram conversation to remain ready to answer any message, the file will be executing infinitely (unless you interrupt it).

But as this solution requires a computer to be always on, I looked for a cloud computing solution. I needed something that could remain on indefinitely but without spending too much money in it. Heroku was the best solution to me as they offer a free project when somebody creates an account. So open an account on Heroku, create a project, push these files into it and enable a worker instance, and your bot should be active on a Heroku instance. 