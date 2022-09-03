import ccxt
import time
import pandas as pd
pd.set_option('display.max_rows', None)
import pandas_ta as ta
import numpy as np
from line_notify import LineNotify 
import configparser
from datetime import datetime as dt
import warnings
warnings.filterwarnings('ignore')
import os
import math 
from tabulate import tabulate
import logging
import mplfinance as mplf

logging.basicConfig(filename='log.log', format='%(asctime)s - %(message)s', level=logging.INFO)
print('VXMA bot (Form Tradingview)By Vaz.')
print('Donate XMR : 87tT3DZqi4mhGuJjEp3Yebi1Wa13Ne6J7RGi9QxU21FkcGGNtFHkfdyLjaPLRv8T2CMrz264iPYQ2dCsJs2MGJ27GnoJFbm')
#call config
config = configparser.ConfigParser()
config.read('config.ini')
#key setting
API_KEY = config['KEY']['API_KEY']
API_SECRET = config['KEY']['API_SECRET']
LINE_TOKEN = config['KEY']['LINE_TOKEN']
notify = LineNotify(LINE_TOKEN)
#Bot setting
USELONG = config['STAT']['Open_LONG']
USESHORT = config['STAT']['Open_SHORT']
USETP = config['STAT']['USE_TP']
USESL = config['STAT']['USE_SL']
Tailing_SL = config['STAT']['Tailing_SL']
MIN_BALANCE = config['STAT']['MIN_BALANCE']
RISK = config['STAT']['LOST_PER_TARDE']
Max_Size = float(config['STAT']['MAX_Margin_USE'])
TPRR1 = config['STAT']['RiskReward_TP1']
TPRR2 = config['STAT']['RiskReward_TP2']
TPPer = int(config['STAT']['Percent_TP1'])
TPPer2 = int(config['STAT']['Percent_TP2'])
Pivot = config['STAT']['Pivot_lookback']
#STAT setting
SYMBOL_NAME = config['BOT']['SYMBOL_NAME'].split(",")
LEVERAGE = config['BOT']['LEVERAGE'].split(",")
TF = config['BOT']['TF'].split(",")
#TA setting
ATR_Period = config['TA']['ATR_Period'].split(",")
ATR_Mutiply = config['TA']['ATR_Mutiply'].split(",")
RSI_Period = config['TA']['RSI_Period'].split(",")
EMA_FAST = config['TA']['EMA_Fast'].split(",")
LINEAR = config['TA']['SUBHAG_LINEAR'].split(",")
SMOOTH = config['TA']['SMOOTH'].split(",")
LengthAO = config['TA']['Andean_Oscillator'].split(",")

BOT_NAME = 'VXMA'
# API CONNECT
exchange = ccxt.binance({
"apiKey": API_KEY,
"secret": API_SECRET,
'options': {
'defaultType': 'future'
},
'enableRateLimit': True
})

Sside = 'BOTH'
Lside = 'BOTH'
messmode = ''
min_balance = 50



currentMODE = exchange.fapiPrivate_get_positionside_dual()
if currentMODE['dualSidePosition']:
    print('You are in Hedge Mode')
    Sside = 'SHORT'
    Lside = 'LONG'
    messmode = 'You are in Hedge Mode'
else:
    print('You are in One-way Mode')
    messmode = 'You are in One-way Mode'

if MIN_BALANCE[0]=='$':
    min_balance=float(MIN_BALANCE[1:len(MIN_BALANCE)])
    print("MIN_BALANCE=",min_balance)

wellcome = 'VXMA Bot Started :\n' + messmode + '\nTrading pair : ' + str(SYMBOL_NAME) + '\nTimeframe : ' + str(TF) + '\nLeverage : ' + str(LEVERAGE) +'\nBasic Setting\n----------\nRisk : ' + str(RISK) + '\nRisk:Reward : ' + str(TPRR1) + '\nATR Period : ' + str(ATR_Period) + '\nATR Multiply : ' + str(ATR_Mutiply) + '\nRSI  : ' + str(RSI_Period) + '\nEMA  : '+ str(EMA_FAST) + '\nLinear : ' + str(LINEAR) + '\nSmooth : ' + str(SMOOTH) + '\nAndean_Oscillator : ' + str(LengthAO) + '\nBot Will Stop Entry when balance < ' + str(min_balance) + '\nGOODLUCK'
notify.send(wellcome)

def candle(df,symbol):
    data = df.tail(365)
    rcs = {"axes.labelcolor":"none",
            "axes.spines.left": False,
            "axes.spines.right": False,
            "axes.titlesize": '20'}
    color = mplf.make_marketcolors(up='green',down='red',volume='inherit',wick='white',edge='white')    
    s = mplf.make_mpf_style(base_mpf_style='nightclouds', rc=rcs ,marketcolors=color,y_on_right=True)
    vxmal = mplf.make_addplot(data.vxma,secondary_y=False,color='yellow')
    mplf.plot(data,type='candle',title=symbol,addplot=vxmal, style=s,volume=True,savefig='candle.png',tight_layout=True)
    notify.send(f'info : {symbol}',image_path=('./candle.png'))
    return 

#clearconsol
def clearconsol():
    time.sleep(5)
    # posix is os name for linux or mac
    if(os.name == 'posix'):
        os.system('clear')
    # else screen will be cleared for windows
    else:
        os.system('cls') 
#Alphatrend
def alphatrend(df,atr_p,atr_m,rsi):
    df['atr'] = ta.sma(ta.true_range(df['High'],df['Low'],df['Close']),atr_p)
    df['rsi'] = ta.rsi(df['Close'],rsi)
    df['downT'] = 0.0
    df['upT'] = 0.0
    df['alphatrend'] = 0.0
#AlphaTrend rsibb >= 50 ? upT < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT : downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT
    for current in range(1, len(df.index)):
        previous = current - 1
        df['downT'][current] = df['High'][current] + df['atr'][current] * atr_m
        df['upT'][current] = df['Low'][current] - df['atr'][current] * atr_m
        if df['rsi'][current] >= 50 :
            if df['upT'][current] < (df['alphatrend'][previous] if df['alphatrend'][previous] != None else 0):
                df['alphatrend'][current] = (df['alphatrend'][previous] if df['alphatrend'][previous] != None else 0)
            else : df['alphatrend'][current] = df['upT'][current]
        else:
            if df['downT'][current] > (df['alphatrend'][previous] if df['alphatrend'][previous] != None else 0):
                df['alphatrend'][current] = (df['alphatrend'][previous] if df['alphatrend'][previous] != None else 0)
            else : df['alphatrend'][current] = df['downT'][current]
    return df
#Andean_Oscillator
def andean(df,AOL):
    df['up1'] = 0.0
    df['up2'] = 0.0
    df['dn1'] = 0.0
    df['dn2'] = 0.0
    df['cmpbull'] = 0.0
    df['cmpbear'] = 0.0
    alpha = 2/(AOL + 1)
    for current in range(1, len(df.index)):
        previous = current - 1
        CloseP = df['Close'][current]
        OpenP = df['Open'][current]
        up1 = df['up1'][previous]
        up2 = df['up2'][previous]
        dn1 = df['dn1'][previous]
        dn2 = df['dn2'][previous]
        # up1 := nz(math.max(C, O, up1[1] - (up1[1] - C) * alpha), C)
        df['up1'][current] = (max(CloseP,OpenP,up1 - (up1 - CloseP)*alpha) if max(CloseP,OpenP,up1 - (up1 - CloseP)*alpha) != None else df['Close'][current])
        # up2 := nz(math.max(C * C, O * O, up2[1] - (up2[1] - C * C) * alpha), C * C)
        df['up2'][current] = (max(CloseP*CloseP,OpenP*OpenP,up2 - (up2 - CloseP*CloseP)*alpha) if max(CloseP*CloseP,OpenP*OpenP,up2 - (up2 - CloseP*CloseP)*alpha) != None else df['Close'][current]*df['Close'][current])
        # dn1 := nz(math.min(C, O, dn1[1] + (C - dn1[1]) * alpha), C)
        df['dn1'][current] = (min(CloseP,OpenP,dn1 + (CloseP - dn1)*alpha) if min(CloseP,OpenP,dn1 + (CloseP - dn1)*alpha) != None else df['Close'][current])
        # dn2 := nz(math.min(C * C, O * O, dn2[1] + (C * C - dn2[1]) * alpha), C * C)
        df['dn2'][current] = (min(CloseP*CloseP,OpenP*OpenP,dn2 + (CloseP*CloseP - dn2)*alpha) if min(CloseP*CloseP,OpenP*OpenP,dn2 + (CloseP*CloseP - dn2)*alpha) != None else df['Close'][current]*df['Close'][current])
        up1n = df['up1'][current] 
        up2n = df['up2'][current]
        dn1n = df['dn1'][current]
        dn2n = df['dn2'][current]
        df['cmpbull'][current] = math.sqrt(dn2n - (dn1n * dn1n))
        df['cmpbear'][current] = math.sqrt(up2n - (up1n * up1n))
    return df
#VXMA Indicator
def vxma(df):
    df['vxma'] = 0.0
    df['trend'] = False
    df['buy'] = False
    df['sell'] = False
    for current in range(2, len(df.index)):
        previous = current - 1
        before  = current - 2
        EMAFAST = df['ema'][current]
        LINREG = df['subhag'][current]
        ALPHATREND = df['alphatrend'][before]
        clohi = max(EMAFAST,LINREG,ALPHATREND)
        clolo = min(EMAFAST,LINREG,ALPHATREND)
            #CloudMA := (bull > bear) ? clolo < nz(CloudMA[1]) ? nz(CloudMA[1]) : clolo :
        if df['cmpbull'][current] > df['cmpbear'][current] :
            if clolo < (df['vxma'][previous] if df['vxma'][previous] != None else 0):
                df['vxma'][current] = (df['vxma'][previous] if df['vxma'][previous] != None else 0)
            else : df['vxma'][current] = clolo
            #  (bear > bull) ? clohi > nz(CloudMA[1]) ? nz(CloudMA[1]) : clohi : nz(CloudMA[1])
        elif df['cmpbull'][current] < df['cmpbear'][current]:
            if clohi > (df['vxma'][previous] if df['vxma'][previous] != None else 0):
                df['vxma'][current] = (df['vxma'][previous] if df['vxma'][previous] != None else 0)
            else : df['vxma'][current] = clohi
        else:
            df['vxma'][current] = (df['vxma'][previous] if df['vxma'][previous] != None else 0)
            #Get trend True = Bull False = Bear
        if df['vxma'][current] > df['vxma'][previous] and df['vxma'][previous] > df['vxma'][before] :
            df['trend'][current] = True
        elif df['vxma'][current] < df['vxma'][previous] and df['vxma'][previous] < df['vxma'][before] :
            df['trend'][current] = False
        else:
            df['trend'][current] = df['trend'][previous] 
            #get zone
        if df['trend'][current] and not df['trend'][previous] :
            df['buy'][current] = True
            df['sell'][current] = False
        elif not df['trend'][current] and df['trend'][previous] :
            df['buy'][current] = False
            df['sell'][current] = True
        else:
            df['buy'][current] = False
            df['sell'][current] = False
    return df
#Pivot High-Low only calculate last fixed bars
def swinghigh(df,Pivot):
    df['Highest'] = df['High']
    for current in range(len(df.index) - int(Pivot), len(df.index)):
        previous = current - 1
        if df['High'][current] > df['Highest'][previous]:
            df['Highest'][current] = df['High'][current]
        else : df['Highest'][current] = df['Highest'][previous]
    highest = df['Highest'][current]
    return highest

def swinglow(df,Pivot):
    df['Lowest'] = df['Low']
    for current in range(len(df.index) - int(Pivot), len(df.index)):
        previous = current - 1
        if df['Low'][current] < df['Lowest'][previous]:
            df['Lowest'][current] = df['Low'][current]
        else : df['Lowest'][current] = df['Lowest'][previous]
    Lowest = df['Lowest'][current]    
    return Lowest

#Build Data Pack for VXMA
def indicator(df,ema_period,linear,smooth,atr_p,atr_m,rsi,AOL):
    df['ema'] = ta.ema(df['Close'],ema_period)
    df['subhag'] = ta.ema(ta.linreg(df['Close'],linear,0),smooth)
    alphatrend(df,atr_p,atr_m,rsi)
    andean(df,AOL)
    vxma(df)
    return df
#Position Sizing
def buysize(df,balance,symbol):
    last = len(df.index) - 1
    freeusd = float(balance['free']['USDT'])
    swinglow = swinglow(df,Pivot)
    if RISK[0]=='$' :
        risk = float(RISK[1:len(RISK)])
    else :
        percent = float(RISK)
        risk = (percent/100)*freeusd
    amount = abs(risk  / (df['Close'][last] - float(swinglow)))
    qty_precision = exchange.markets[symbol]['precision']['amount']
    lot = round(amount,qty_precision)
    return lot

def sellsize(df,balance,symbol):
    last = len(df.index) - 1
    freeusd = float(balance['free']['USDT'])
    swinghigh = swinghigh(df,Pivot)
    if RISK[0]=='$' :
        risk = float(RISK[1:len(RISK)])
    else :
        percent = float(RISK)
        risk = (percent/100)*freeusd
    amount = abs(risk  / (float(swinghigh) - df['Close'][last]))
    qty_precision = exchange.markets[symbol]['precision']['amount']
    lot = round(amount,qty_precision)
    return lot
#TP with Risk:Reward    
def RRTP(df,symbol,direction,step):
    if direction :
        if step == 1 :
            ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
            target = ask *(1+((ask-df['Lowest'][len(df.index)-1])/ask)*float(TPRR1))
        if step == 2 :
            ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
            target = ask *(1+((ask-df['Lowest'][len(df.index)-1])/ask)*float(TPRR2))
    else :
        if step == 1 :
            bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
            target = bid *(1-((df['Highest'][len(df.index)-1]-bid)/bid)*float(TPRR1))
        if step == 2 :
            bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
            target = bid *(1-((df['Highest'][len(df.index)-1]-bid)/bid)*float(TPRR2))    
    return target

def RR1(df,symbol,direction):
    if direction :
        ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
        target = ask *(1+((ask-df['Lowest'][len(df.index)-1])/ask)*1)
    else :
        bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
        target = bid *(1-((df['Highest'][len(df.index)-1]-bid)/bid)*1)
    return target

def callbackRate(df):
    rate = round((df['Highest'][len(df.index)-1]-df['Lowest'][len(df.index)-1])/df['Highest'][len(df.index)-1]*100,1)
    if rate > 5 :
        rate = 5
    elif rate < 0.1 :
        rate = 0.1
    return rate 

#OpenLong=Buy
def OpenLong(df,balance,symbol,lev):
    print('Entry Long')
    amount = float(buysize(df,balance,symbol))
    ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
    try:
        exchange.set_leverage(lev,symbol)
    except:
        time.sleep(1)
        lever = exchange.fetch_positions_risk([symbol])
        for x in range(len(lever)):
            if (lever[x]['symbol']) == symbol:
                lev = round(lever[x]['leverage'],0)
                print(lev)
                exchange.set_leverage(int(lev),symbol)
                break
    if amount*ask > Max_Size*int(lev):
        amount = Max_Size*int(lev)/ask  
    free = float(balance['free']['USDT'])
    amttp1 = amount*(TPPer/100)
    amttp2 = amount*(TPPer2/100)
    swinglow = swinglow(df,Pivot)
    if free > min_balance :
        try:
            order = exchange.createMarketOrder(symbol,'buy',amount,params={'positionSide':Lside})
            logging.info(order)
        except ccxt.InsufficientFunds as e:
            logging.debug(e)
            return    
        if USESL :
            if currentMODE['dualSidePosition']:
                orderSL         = exchange.create_order(symbol,'stop','sell',amount,float(swinglow),params={'stopPrice':float(swinglow),'triggerPrice':float(swinglow),'positionSide':Lside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol, 'TRAILING_STOP_MARKET','sell',amount,params ={'activationPrice':float(RR1(df,symbol,True)) ,'callbackRate': float(callbackRate(df)),'positionSide':Lside})
            else:
                orderSL         = exchange.create_order(symbol,'stop','sell',amount,float(swinglow),params={'stopPrice':float(swinglow),'triggerPrice':float(swinglow),'reduceOnly': True ,'positionSide':Lside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol, 'TRAILING_STOP_MARKET','sell',amount,params ={'activationPrice':float(RR1(df,symbol,True)) ,'callbackRate': float(callbackRate(df)),'reduceOnly': True ,'positionSide':Lside})
            if Tailing_SL :
                logging.info(ordertailingSL)
            logging.info(orderSL)
        if USETP :
            orderTP  = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','sell',amttp1,float(RRTP(df,symbol,True,1)),params={'stopPrice':float(RRTP(df,symbol,True,1)),'triggerPrice':float(RRTP(df,symbol,True,1)),'positionSide':Lside})
            orderTP2 = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','sell',amttp2,float(RRTP(df,symbol,True,2)),params={'stopPrice':float(RRTP(df,symbol,True,2)),'triggerPrice':float(RRTP(df,symbol,True,2)),'positionSide':Lside})
            logging.info(orderTP)
            logging.info(orderTP2)
        time.sleep(1)
        margin=ask*amount/lev
        total = float(balance['total']['USDT'])
        msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "OpenLong[BUY]" + "\nAmount    : " + str(amount) +"("+str(round((amount*ask),2))+" USDT)" + "\nPrice        :" + str(ask) + " USDT" + str(round(margin,2))+  " USDT"+ "\nBalance   :" + str(round(total,2)) + " USDT"
    else :
        msg = "MARGIN-CALL!!!\nยอดเงินต่ำกว่าที่กำหนดไว้  : " + str(min_balance) + '\nยอดปัจจุบัน ' + str(round(free,2)) + ' USD\nบอทจะทำการยกเลิกการเข้า Position ทั้งหมด' 
    notify.send(msg)
    candle(df,symbol)
    #clearconsol()
    return

#OpenShort=Sell
def OpenShort(df,balance,symbol,lev):
    print('Entry Short')
    amount = float(buysize(df,balance,symbol))
    bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
    try:
        exchange.set_leverage(lev,symbol)
    except:
        time.sleep(1)
        lever = exchange.fetch_positions_risk([symbol])
        for x in range(len(lever)):
            if (lever[x]['symbol']) == symbol:
                lev = round(lever[x]['leverage'],0)
                print(lev)
                exchange.set_leverage(int(lev),symbol)
                break
    if amount*bid > Max_Size*int(lev):
        amount = Max_Size*int(lev)/bid  
    free = float(balance['free']['USDT'])
    amttp1 = amount*(TPPer/100)
    amttp2 = amount*(TPPer2/100)
    swinghigh = swinghigh(df,Pivot)
    if free > min_balance :
        try:
            order = exchange.createMarketOrder(symbol,'sell',amount,params={'positionSide':Sside})
            logging.info(order)
        except ccxt.InsufficientFunds as e:
            logging.debug(e)
            return        
        if USESL :
            if currentMODE['dualSidePosition']:
                orderSL         = exchange.create_order(symbol,'stop','buy',amount,float(swinghigh),params={'stopPrice':float(swinghigh),'triggerPrice':float(swinghigh),'positionSide':Sside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol,'TRAILING_STOP_MARKET','buy',amount,params ={'activationPrice':float(RR1(df,symbol,False)) ,'callbackRate': float(callbackRate(df)),'positionSide':Sside})
            else :
                orderSL         = exchange.create_order(symbol,'stop','buy',amount,float(swinghigh),params={'stopPrice':float(swinghigh),'triggerPrice':float(swinghigh),'reduceOnly': True ,'positionSide':Sside})
                if Tailing_SL :
                    ordertailingSL  = exchange.create_order(symbol,'TRAILING_STOP_MARKET','buy',amount,params ={'activationPrice':float(RR1(df,symbol,False)) ,'callbackRate': float(callbackRate(df)),'reduceOnly': True ,'positionSide':Sside})
            if Tailing_SL :    
                logging.info(ordertailingSL)
            logging.info(orderSL)
        if USETP :
            orderTP = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','buy',amttp1,float(RRTP(df,symbol,False,1)),params={'stopPrice':float(RRTP(df,symbol,False,1)),'triggerPrice':float(RRTP(df,symbol,False,1)),'positionSide':Sside})
            logging.info(orderTP)
            orderTP2 = exchange.create_order(symbol,'TAKE_PROFIT_MARKET','buy',amttp2,float(RRTP(df,symbol,False,2)),params={'stopPrice':float(RRTP(df,symbol,False,2)),'triggerPrice':float(RRTP(df,symbol,False,2)),'positionSide':Sside})
            logging.info(orderTP2)
        time.sleep(1)
        margin=bid*amount/lev
        total = float(balance['total']['USDT'])
        msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "OpenShort[SELL]" + "\nAmount    : " + str(amount) +"("+str(round((amount*bid),2))+" USDT)" + "\nPrice        :" + str(bid) + " USDT" + str(round(margin,2))+  " USDT"+ "\nBalance   :" + str(round(total,2)) + " USDT"
    else :
        msg = "MARGIN-CALL!!!\nยอดเงินต่ำกว่าที่กำหนดไว้  : " + str(min_balance) + '\nยอดปัจจุบัน ' + str(round(free,2)) + ' USD\nบอทจะทำการยกเลิกการเข้า Position ทั้งหมด' 
    notify.send(msg)
    candle(df,symbol)
    # clearconsol()
    return
#CloseLong=Sell
def CloseLong(df,balance,symbol,amt,pnl):
    print('Close Long')
    amount = abs(amt)
    upnl = pnl
    bid = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['bidPrice'])
    order = exchange.createMarketOrder(symbol,'sell',amount,params={'positionSide':Lside})
    time.sleep(1)
    logging.info(order)
    total = float(balance['total']['USDT'])
    msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "CloseLong[SELL]" + "\nAmount    : " + str(amount) +"("+str(round((amount*bid),2))+" USDT)" + "\nPrice        :" + str(bid) + " USDT" + "\nRealized P/L: " + str(round(upnl,2)) + " USDT"  +"\nBalance   :" + str(round(total,2)) + " USDT"
    notify.send(msg)
    candle(df,symbol)
    # clearconsol()
    return
#CloseShort=Buy
def CloseShort(df,balance,symbol,amt,pnl):
    print('Close Short')
    amount = abs(amt)
    upnl = pnl
    ask = float(exchange.fetchBidsAsks([symbol])[symbol]['info']['askPrice'])
    order = exchange.createMarketOrder(symbol,'buy',amount,params={'positionSide':Sside})
    time.sleep(1)
    logging.info(order)
    total = float(balance['total']['USDT'])
    msg ="BINANCE:\n" + "BOT         : " + BOT_NAME + "\nCoin        : " + symbol + "\nStatus      : " + "CloseShort[BUY]" + "\nAmount    : " + str(amount) +"("+ str(round((amount*ask),2))+" USDT)" + "\nPrice        :" + str(ask) + " USDT" + "\nRealized P/L: " + str(round(upnl,2)) + " USDT"  +"\nBalance   :" + str(round(total,2)) + " USDT"
    notify.send(msg)
    candle(df,symbol)
    # clearconsol()
    return

def check_buy_sell_signals(df,symbol,status,balance,lev):
    is_in_Long = False
    is_in_Short = False
    is_in_position = False
    last = len(df.index) -1
    previous = last - 1
    posim = symbol.replace('/','')
    amt = 0.0
    upnl = 0.0
    for i in status.index:
        if status['symbol'][i] == posim:
            amt = float(status['positionAmt'][i])
            upnl = float(status['unrealizedProfit'][i])
            print(amt)
            break
    # NO Position
    if not status.empty and amt != 0 :
        is_in_position = True
    else: 
        is_in_position = False
        is_in_Short = False
        is_in_Long = False
    # Long position
    if is_in_position and amt > 0  :
        is_in_Long = True
        is_in_Short = False
    # Short position
    if is_in_position and amt < 0  :
        is_in_Short = True
        is_in_Long = False  
    print("checking for buy and sell signals")
    if df['buy'][last] :
        print("changed to Bullish, buy")
        if is_in_Short :
            CloseShort(df,balance,symbol,amt,upnl)
        if not is_in_Long and USELONG:
            exchange.cancel_all_orders(symbol)
            time.sleep(1)
            OpenLong(df,balance,symbol,lev)
            is_in_Long = True
        else:
            print("already in position, nothing to do")
    if df['sell'][last]:
        print("changed to Bearish, Sell")
        if is_in_Long :
            CloseLong(df,balance,symbol,amt,upnl)
        if not is_in_Short and USESHORT :
            exchange.cancel_all_orders(symbol)
            time.sleep(1)
            OpenShort(df,balance,symbol,lev)
            is_in_Short = True
        else:
            print("already in position, nothing to do")

def main():
    balance = exchange.fetch_balance()    
    exchange.precisionMode = ccxt.DECIMAL_PLACES
    positions = balance['info']['positions']
    for i in range(len(SYMBOL_NAME)):
        symbol = SYMBOL_NAME[i] + "/USDT"
        leverage = int(LEVERAGE[i])
        ema = int(EMA_FAST[i])
        linear = int(LINEAR[i])
        smooth = int(SMOOTH[i])
        atr_p = int(ATR_Period[i])
        atr_m = float(ATR_Mutiply[i])
        rsi = int(RSI_Period[i])
        AOL = int(LengthAO[i])
        tf = TF[i]
        current_positions = [position for position in positions if float(position['positionAmt']) != 0]
        position_bilgi = pd.DataFrame(current_positions, columns=["symbol", "entryPrice","positionSide", "unrealizedProfit", "positionAmt", "initialMargin" ,"isolatedWallet"])
        exchange.load_markets()
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, since = None, limit = 1002)
        df = pd.DataFrame(bars[:-1], columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('timestamp')
        indicator(df,ema,linear,smooth,atr_p,atr_m,rsi,AOL)
        print('checking current position on hold...')
        print(tabulate(position_bilgi, headers = 'keys', tablefmt = 'grid'))
        print(f"Fetching new bars for {symbol , tf , dt.now().isoformat()}")
        check_buy_sell_signals(df,symbol,position_bilgi,balance,leverage)

if __name__ == "__main__":
    while True:
        main()
