#Date 2018.10.30
#Version 1.6

# IMPORT MODULES
#-----------------------
import requests
import statistics
import math
import time
import datetime
import os

# DEFINE VARIABLES
#-----------------------
step_mode = 1
noise_mode = 0
use_current_price = 0
order_buy_max_price = 0.0003
order_sell_min_price = 0.0002
order_buy_override_price = 0
order_sell_override_price = 0
coin1_noise_unit = 0.000001 #+-
coin1_noise_unit_shift = 0 # negative buys lower and sells lower / positive buys higher and sells higher
SleepTime = 60
TestMode = 0

# DEFINE CURRENCIES
#-----------------------
coin1 = 'STAK'
coin2 = 'ETH'
coin_pair = coin1 + '-' + coin2

# DEFINE CURRENCY VALUE SETTINGS
#-----------------------
coin_settings = {
    'R-ETH': {'order_average_price': 0.000715, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 10, 'coin2_min_trade_amount': 0.005},
    'RNTB-ETH': {'order_average_price': 0.0000450, 'coin_min_unit': 0.0000001, 'coin1_min_trade_amount': 100, 'coin2_min_trade_amount': 0.005},
    'HGT-ETH': {'order_average_price': 0.000023, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 100, 'coin2_min_trade_amount': 0.005},
    'MORPH-ETH': {'order_average_price': 0.000030, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 10, 'coin2_min_trade_amount': 0.005},
    'NET-ETH': {'order_average_price': 0.000850, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 10, 'coin2_min_trade_amount': 0.005},
	'SUNC-ETH': {'order_average_price': 0.000005, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 10, 'coin2_min_trade_amount': 0.005},
	'STAK-ETH': {'order_average_price': 0.00023, 'coin_min_unit': 0.000001, 'coin1_min_trade_amount': 10, 'coin2_min_trade_amount': 0.003}
}

#order_buy_price = coin_settings[coin_pair]['order_average_price'] + coin_settings[coin_pair]['coin_min_unit']
#order_sell_price = coin_settings[coin_pair]['order_average_price'] - coin_settings[coin_pair]['coin_min_unit']
coin1_min_trade_amount = coin_settings[coin_pair]['coin1_min_trade_amount']
coin2_min_trade_amount = coin_settings[coin_pair]['coin2_min_trade_amount']
coin2_Safety_Untreadeable = 0.003

# AUTHENTICATE
#-----------------------
script_dir = os.path.dirname(__file__)
filename = os.path.join(script_dir, 'PrivateKey.txt')
with open(filename) as file:
    auth_key = file.read().splitlines()
file.close()

API = auth_key[0]
KEY = auth_key[1]
session = requests.session()
session.auth = (API, KEY)

r = session.delete('https://api.hitbtc.com/api/2/order')
time.sleep(1)

# GET COIN MARKET DATA
#-----------------------
candles = {'period': 'M1', 'limit': '3'}
r = session.get('https://api.hitbtc.com/api/2/public/candles/' + coin1 + coin2, params = candles)
data = r.json()

o1_now = float(data[0]['open'])
c1_now = float(data[0]['close'])
price_list_now = [o1_now, c1_now]
mean_price_lagged = round(statistics.mean(price_list_now), 9)
price_now = abs(o1_now - c1_now)

Price_list_bid = list();
Price_list_ask = list();

r = session.get('https://api.hitbtc.com/api/2/public/ticker/' + coin1 + coin2)
data = r.json()

bid_price = float(data['bid'])
ask_price = float(data['ask'])

Price_list_bid.append(bid_price)
Price_list_ask.append(ask_price)

loop = 1
#loop2 = 1
while loop < 1000000:
#while loop < 2:

	# GET COIN MARKET DATA
	#-----------------------
	candles = {'period': 'M1', 'limit': '3'}
	r = session.get('https://api.hitbtc.com/api/2/public/candles/' + coin1 + coin2, params = candles)
	data = r.json()

	o1_now = float(data[0]['open'])
	c1_now = float(data[0]['close'])
	price_list_now = [o1_now, c1_now]
	mean_price_lagged = round(statistics.mean(price_list_now), 9)
	price_now = abs(o1_now - c1_now)

	if use_current_price == 1:
		coin_settings[coin_pair]['order_average_price'] = price_now

	print('DateStamp : 		' + str(datetime.datetime.now()))
	print('Iteration : 		' + str(loop))

	r = session.get('https://api.hitbtc.com/api/2/public/ticker/' + coin1 + coin2)
	data = r.json()

	bid_price = float(data['bid'])
	ask_price = float(data['ask'])
	Price_list_bid.append(bid_price)
	Price_list_ask.append(ask_price)

	order_buy_price = bid_price
	order_sell_price = ask_price

	#Real_coin1_noise_unit = price_now/2
	#if Real_coin1_noise_unit > coin1_noise_unit:
	#	coin1_noise_unit = Real_coin1_noise_unit

	# DELETE ALL ACTIVE ORDERS IF NEW COIN BID/ASK PRICES ARE NOT THE SAME AS PREVIOUS
	#-----------------------
	if Price_list_bid[loop] != Price_list_bid[loop-1] or Price_list_ask[loop] != Price_list_ask[loop-1]:
		r = session.delete('https://api.hitbtc.com/api/2/order')
		print('---- Cancelled orders ----')

		time.sleep(1)

	# GET WALLET DATA
	#-----------------------
	r = session.get('https://api.hitbtc.com/api/2/trading/balance')
	data2 = r.json()
	#print(data2)

	coin1_data = next((item for item in data2 if item['currency'] == coin1), None)
	coin1_balance = float(coin1_data['available'])

	coin2_data = next((item for item in data2 if item['currency'] == coin2), None)
	coin2_balance = float(coin2_data['available'])

	print('coin1 balance : 	' + str(coin1_balance) + ' ' + coin1)
	print('coin2 balance : 	' + str(coin2_balance) + ' ' + coin2)

	if noise_mode == step_mode:
		raise Exception('Noise/Step modes both on')

	# BUY/SELL PRICING LOGIC
	#-----------------------
	if noise_mode == 1:
		order_buy_price = bid_price - (coin1_noise_unit - coin1_noise_unit_shift)
		order_sell_price = ask_price + (coin1_noise_unit + coin1_noise_unit_shift)

	if step_mode == 1:
		if bid_price != order_buy_max_price:
			order_buy_price = order_buy_max_price - (coin1_noise_unit - coin1_noise_unit_shift)
		if ask_price != order_sell_min_price:
			order_sell_price = order_sell_min_price + (coin1_noise_unit - coin1_noise_unit_shift)

	if order_buy_max_price != 0:
		if order_buy_price > order_buy_max_price:
			order_buy_price = order_buy_max_price
		if order_sell_price < order_sell_min_price:
			order_sell_price = order_sell_min_price

	# If the order buy/sell price is not below/above the current price, decrease/increase to current price
	if order_buy_price > bid_price:
		order_buy_price = bid_price
	if order_sell_price < ask_price:
		order_sell_price = ask_price

	if order_buy_override_price != 0:
		order_buy_price = order_buy_override_price
		order_sell_price = order_sell_override_price

	print('Bid price : 		' + str(bid_price))
	print('Ask price : 		' + str(ask_price))
	#print('Real coin noise unit : 	' + str(Real_coin1_noise_unit))
	print('Coin noise unit : 	' + str(coin1_noise_unit))
	print('Coin buy price : 	' + str(order_buy_price))
	print('Coin sell price : 	' + str(order_sell_price))

	if TestMode != 0:
		time.sleep(999999)

	# Estimate how much coins available to buy
	if coin2_balance >= coin2_min_trade_amount:
	# Initial coin1 balance - 1%
		#Available_to_buy = math.floor(((coin2_balance - (coin2_balance*0.005)) / order_buy_price)/coin1_min_trade_amount)*coin1_min_trade_amount
		Available_to_buy = math.floor(((coin2_balance-coin2_Safety_Untreadeable) / order_buy_price)/coin1_min_trade_amount)*coin1_min_trade_amount
	else:
		Available_to_buy = 0

	print('Available to buy : 	' + str(Available_to_buy))

	# PLACE ORDERS
	#-----------------------
	if Available_to_buy > 0:
		orderData = {'symbol': coin1 + coin2, 'side': 'buy', 'quantity': Available_to_buy, 'price': order_buy_price }
		r = session.post('https://api.hitbtc.com/api/2/order', data = orderData)
		data = r.json()
		print('Buy order : 		' + str(Available_to_buy) + ' ' + coin1)
		print('Buy price : 		' + str(order_buy_price) + ' ' + coin2)

	if coin1_balance >= coin1_min_trade_amount:
		orderData = {'symbol': coin1 + coin2, 'side': 'sell', 'quantity': coin1_balance, 'price': order_sell_price }
		r = session.post('https://api.hitbtc.com/api/2/order', data = orderData)
		data = r.json()

		print('Sell order : 		' + str(coin1_balance) + ' ' + coin1)
		print('Sell price : 		' + str(order_sell_price) + ' ' + coin2)

	print('------------------------------------')

	time.sleep(SleepTime)

	loop = loop + 1
