#VXMA BOT TRADING STRATEGY BY VAZ.
```
What's this version do?
|-v.0.1 	= Start from VXMA Pinescript Tradingview.
|-v.1.0.0	= Start Deploy Fully-Function
|-v.1.0.1	= Fix order params and add TP/SL Order
|-v.1.1		= Fix config.ini found '\n'
|-V.1.2		= BUY AND SELL SWITCH 
|- 			+TP AND SL SWITCH 
|- 			+TP2
|- 			+Try Improve BUY SELL condition and detail
|-v.1.2.1 = fix TP formula.
|-v.1.2.2 = TailingStopMarket order fully-function.
|- 			
|-v2.0
|- Avoid Large Position amount
|- Input Max margin use
|- แจ้งเตือนยอดเงินทุกชั่วโมง
```
##สามารถตั้งค่าได้ดังต่อไปนี้นี้
```
[KEY]
API_KEY = 
API_SECRET = 
LINE_TOKEN = 
[STAT]
OPEN_LONG = True
OPEN_SHORT = True
USE_TP = True
USE_SL = True
Tailing_SL = True
MIN_BALANCE = $50
LOST_PER_TARDE = $10 
MAX_Margin_USE = $5
RiskReward = 3
TP_Percent = 50
Pivot_lookback = 50
[BOT]
SYMBOL_NAME = BTC,BTC,BTC
LEVERAGE = 125,125,125
TF = 15m,4h,1d
[TA]
ATR_Period = 12,19,7
ATR_Mutiply = 1.6,2,3
RSI_Period = 25,25,25
EMA_Fast = 30,30,40
SUBHAG_LINEAR = 30,30,30
SMOOTH = 30,30,30
Andean_Oscillator = 30,30,30
```
ในหัวข้อ [BOT] และ [TA] สามารถตั้งได้หลาย ๆ ค่าด้วย คอมม่า  (  , ) 
โดยจะต้องเรียงลำดับตามที่ต้องการ  (leverage 1,2,3,4 = symbol 1,2,3,4)
##LOST_PER_TARDE  
```
ถ้าอยากใช้ % ให้ใช้ตัวเลขธรรมดา 	 LOST_PER_TARDE = 5
ถ้าอยากใช้ $ ให้ใช้ $ นำหน้า		LOST_PER_TARDE = $10
```
###Donate XMR : 87tT3DZqi4mhGuJjEp3Yebi1Wa13Ne6J7RGi9QxU21FkcGGNtFHkfdyLjaPLRv8T2CMrz264iPYQ2dCsJs2MGJ27GnoJFbm
