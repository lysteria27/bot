import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

socket = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m" # /ws/<symbol>@kline_<interval>

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL =  'ETHUSD'
TRADE_QUANTITY = 0.05

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        #print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("closed connection")

def on_message(ws, message):
    global closes

    print("received message")
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']

    candle_closed = candle['x']
    close = candle['c']

    if candle_closed:
        closes.append(float(close))
        print("Candle closed at {}".format(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current RSI is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell!!!")
                    #put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False

                else:
                    print("It is overbought, but we don't own any. Nothing to do")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it. Nothing to do")
                else:
                    print("Oversold! Buy!!!")
                    #put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True

ws = websocket.WebSocketApp(socket, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()