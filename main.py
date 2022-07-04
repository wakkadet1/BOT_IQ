from iqoptionapi.stable_api import IQ_Option
import time
import iq
import binary_star
from configparser import ConfigParser
from line_notify import LineNotify
from prettytable import PrettyTable





iq.exp()

dbconf = ConfigParser()
dbconf.read_file(open(r'config.ini'))

Line = dbconf.get('Login', 'Line')

ModeMoney = int(dbconf.get('Mode', 'ModeMoney'))
Mode = int(dbconf.get('Mode', 'Mode'))
Mode_new = int(dbconf.get('Mode', 'Mode_new'))

Timelimit = int(dbconf.get('Trade', 'Timelimit'))
Timeframe = int(dbconf.get('Trade', 'Timeframe'))
Amount = int(dbconf.get('Trade', 'Amount'))
Assets = dbconf.get('Trade', 'Asset').split(",")
Currency_new = dbconf.get('Trade', 'Currency_new').split(",")
Martingale = float(dbconf.get('Trade', 'Martingale'))
RoundMartingale = int(dbconf.get('Trade', 'RoundMartingale'))
TP = int(dbconf.get('Trade','TP'))
SL = int(dbconf.get('Trade','SL'))



notify = LineNotify(Line)
CANDLE_NUMBER = 1000

ema_cross = 0
macd_cross = 0
adx_cross = 0

AA=0
AB=0
loss=0

if ModeMoney == 1:
    ModeMoney = "PRACTICE"
elif ModeMoney == 2:
    ModeMoney = "REAL"

api_iq = iq.login(IQ_Option,ModeMoney)
balance = api_iq.get_balance()
gs = api_iq.get_balance()
tg = balance + TP
sl = balance - SL
#assets1 = iq.load_goals(api_iq)
print(Assets)
print(Currency_new)
#print(assets1)
while True:
    while int(time.localtime().tm_sec % 60) < 2:
        start = time.process_time()
        time_string = time.strftime("%d/%m/%Y %H:%M",time.localtime())
        print(".................................................")
        print(time_string)

        data = PrettyTable()
        data1 = PrettyTable()
        data.field_names = ["Assets", "AO", "MACD", "ADX","UO","EMA"]
        data1.field_names = ["Assets", "AO", "MACD","MACD_signal", "ADX","ADX+","ADX-","UO","EMA"]
        if Mode_new == 1 :
            time_new = time.strftime("%Y-%m-%d %H:%M:%S")
            for asset in Currency_new:
                for i in asset:
                    news = iq.data_news(i)
                    if news != None:
                        for i in news:
                            if time_new == i['date'] and float(i['star']) > 1 and i['currency'] in CA:
                                print("NEWS")
                                time.sleep(3600)

        for asset in Assets:

            #print(asset)
            goal_asset = iq.rename_data(api_iq.get_candles(asset,Timeframe, CANDLE_NUMBER, time.time()))
            #print(time.time())
            #print(goal_asset1)
            target_df = iq.get_indicators(goal_asset)





            ema =binary_star.ema(target_df)
            macd_cross = binary_star.macd_cross(target_df)
            adx_cross = binary_star.adx_cross(target_df)
            ao = binary_star.AO(target_df)
            #rsi = binary_star.RSI(target_df)
            uo = binary_star.UO(target_df)
            data.add_row([asset,ao,macd_cross,adx_cross,uo,ema])

            #print("ADX: ", target_df['ADX'].iloc[-1])
            #print("ADXM: ", target_df['minus'].iloc[-1])
            #print("ADXP: ", target_df['plus'].iloc[-1])

            data1.add_row([asset,round(target_df['AO'].iloc[-1],8),
                           round(target_df['MACD'].iloc[-1],8),
                           round(target_df['MACD_signal'].iloc[-1],8),
                           round(target_df['ADX'].iloc[-1]+5,8),
                           round(target_df['plus'].iloc[-1],8),
                           round(target_df['minus'].iloc[-1],8),
                           round(target_df['UO'].iloc[-1],8),
                           round(target_df['EMA'].iloc[-1],8)])

            #data1.add_row([asset,target_df['AO'].iloc[-1],
            #               target_df['MACD'].iloc[-1],
            #               target_df['MACD_signal'].iloc[-1],
            #               target_df['ADX'].iloc[-1],
            #               target_df['plus'].iloc[-1],
            #               target_df['minus'].iloc[-1],
            #               target_df['UO'].iloc[-1],
            #               target_df['EMA'].iloc[-1]])

            #data1.add_row([asset,
            #               logsumexp(target_df['AO'].iloc[-1]),
            #               logsumexp(target_df['MACD'].iloc[-1]),
            #               logsumexp(target_df['MACD_signal'].iloc[-1]),
            #               logsumexp(target_df['ADX'].iloc[-1]),
            #               logsumexp(target_df['plus'].iloc[-1]),
            #               logsumexp(target_df['minus'].iloc[-1]),
            #               logsumexp(target_df['UO'].iloc[-1]),
            #               logsumexp(target_df['EMA'].iloc[-1])])





            if(Mode == 1):
                # Strategy Call
                if ao == 1 and macd_cross == 1 and adx_cross == 1 and uo == 1 and ema == 1:
                    opensell,id = api_iq.buy_digital_spot(asset,Amount,'call',Timelimit)
                    print('Buying:', asset,' Amount: ',Amount, ' ID: ', id)
                    if opensell == True:
                        while True:
                            check, win = api_iq.check_win_digital_v2(id)
                            if check:
                                break
                        if win > 0:
                            AA += 1
                            loss = 0
                            Amount = int(dbconf.get('Trade', 'Amount'))
                            print("WIN :", '%.2f' % win)
                            gs = api_iq.get_balance()
                            notify.send("\n" + asset + "\nWin : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit: '+ '{:.2f}'.format(gs-balance))
                        elif loss <= RoundMartingale and win<0:
                            AB += 1
                            print("LOSS :", '%.2f' % win)
                            Amount = Amount * Martingale
                            loss +=1
                            gs = api_iq.get_balance()
                            notify.send("\n" + asset + "\nLoss : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit: '+ '{:.2f}'.format(gs-balance))
#
                 # Strategy Put
                if ao == -1 and macd_cross == -1 and adx_cross == -1 and uo==-1 and ema == -1:
                    opensell,id = api_iq.buy_digital_spot(asset,Amount, 'put',Timelimit)
                    print('Selling:', asset,' Amount: ',Amount, ' ID: ', id)
                    if opensell == True:
                        while True:
                            check, win = api_iq.check_win_digital_v2(id)
                            if check:
                                break
                        if win > 0:
                            AA += 1
                            loss = 0
                            Amount = int(dbconf.get('Trade', 'Amount'))
                            print("WIN :", '%.2f' % win)
                            gs = api_iq.get_balance()
                            notify.send("\n" + asset + "\nWin : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit: '+ '{:.2f}'.format(gs-balance))
                        elif loss <= RoundMartingale and win<0:
                            AB += 1
                            print("LOSS :", '%.2f' % win)
                            Amount = Amount * Martingale
                            loss +=1
                            gs = api_iq.get_balance()
                            notify.send("\n" + asset + "\nLoss : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit: '+ '{:.2f}'.format(gs-balance))

            elif(Mode == 2):
                # Strategy Call
                if ao == 1 and macd_cross == 1 and adx_cross == 1 and uo == 1:
                    opensell, id = api_iq.buy(Amount, asset, 'call',Timelimit)
                    print('Buying:', asset, ' Amount: ', Amount, ' ID: ', id)
                    win = api_iq.check_win_v3(id)
                    if win > 0:
                        AA += 1
                        loss = 0
                        Amount = int(dbconf.get('Trade', 'Amount'))
                        print("WIN :", '%.2f' % win)
                        gs = api_iq.get_balance()
                        notify.send("\n" + asset + "\nWin : " + '{:.2f}'.format(win) + f"{api_iq.get_currency()}" + '\nProfit:' + '{:.2f}'.format(gs - balance))
                    elif loss <= RoundMartingale and win < 0:
                        AB += 1
                        print("LOSS :", '%.2f' % win)
                        Amount = Amount * Martingale
                        loss += 1
                        gs = api_iq.get_balance()
                        notify.send("\n" + asset + "\nLoss : " + '{:.2f}'.format(win) + f"{api_iq.get_currency()}" + '\nProfit:' + '{:.2f}'.format(gs - balance))
                if ao == -1 and macd_cross == -1 and adx_cross == -1 and uo == -1:
                    opensell, id = api_iq.buy(Amount,asset,'put',Timelimit)
                    print('Selling:', asset, ' Amount: ', Amount, ' ID: ', id)
                    win = api_iq.check_win_v3(id)
                    if win > 0:
                        AA += 1
                        loss = 0
                        Amount = int(dbconf.get('Trade', 'Amount'))
                        print("WIN :", '%.2f' % win)
                        gs = api_iq.get_balance()
                        notify.send("\n" + asset + "\nWin : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit:'+ '{:.2f}'.format(gs-balance))
                    elif loss <= RoundMartingale and win<0:
                        AB += 1
                        print("LOSS :", '%.2f' % win)
                        Amount = Amount * Martingale
                        loss +=1
                        gs = api_iq.get_balance()
                        notify.send("\n" + asset + "\nLoss : " + '{:.2f}'.format(win)+f"{ api_iq.get_currency()}"+'\nProfit:'+ '{:.2f}'.format(gs-balance))

        # Setting goals by profit
        print(data1)
        print(data)
        timeToSleep = 60 - time.localtime().tm_sec - 1
        print('Waiting next candles ', timeToSleep, " seconds.\n")
        print(f"Balance : {api_iq.get_balance()} {api_iq.get_currency()}")
        print("WIN", AA, "LOSS", AB)
        print("Profit: {:.2f}".format(gs-balance))
        print(".................................................")
        print('')
        if balance >= tg:
            print("TP",TP,f"blance : {API.get_balance()} {api_iq.get_currency()}")
            M = 1
            break
        if balance <= sl:
            print("SL",SL,f"blance : {API.get_balance()} {api_iq.get_currency()}")
            M = 1
            break
        time.sleep(timeToSleep)
        break