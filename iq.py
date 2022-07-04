import time
import numpy as np
import pandas as pd
import ta as tafin
from finta import TA
from configparser import ConfigParser
from bs4 import BeautifulSoup as bts
import requests
import datetime
from string import Formatter
from tkinter import messagebox
from tkinter import *


dbconf = ConfigParser()
dbconf.read_file(open(r'config.ini'))

def load_goals(iq):
    '''
    Gets open instruments and their profit from IQ
    '''

    profits_from_iq = iq.get_all_profit()
    assets_from_iq = iq.get_all_open_time()

    #inst = {i: profits_from_iq[i]['turbo'] for i in assets_from_iq['turbo'] if
    #       assets_from_iq['turbo'][i]['open'] == True}

    inst = [i for i in assets_from_iq['turbo'] if
            assets_from_iq['turbo'][i]['open'] == True]
    print(inst)
    return inst


def rename_data(candles):
    '''
    Renames some df columns in order to calculate some indicators

    '''

    df = pd.DataFrame(candles).rename(columns={'max': 'high', 'min': 'low'})
    return df

def candles(RTCD):


    df = {
        'open': np.array([]),
        'high': np.array([]),
        'low': np.array([]),
        'close': np.array([]),
        'volume': np.array([])}
    for RTCDS in list(RTCD):
        df["open"] = np.append(df["open"], RTCD[RTCDS]["open"])
        df["close"] = np.append(df["open"], RTCD[RTCDS]["close"])
        df["high"] = np.append(df["open"], RTCD[RTCDS]["max"])
        df["low"] = np.append(df["open"], RTCD[RTCDS]["min"])
        df["volume"] = np.append(df["open"], RTCD[RTCDS]["volume"])

    return df


def get_indicators(df):
    '''
    Calculates and returns the following indicators from the df given:

        ADX:
            period = 14
        EMAs:
            means 9, 12, 26, 100
        MACD:
            period_fast = 12
            period_slow = 26
            signal = 9

    '''
    period_adx = int(dbconf.get('Indicator', 'period_adx'))#14
    period_ema = int(dbconf.get('Indicator', 'period_ema'))#10
    period_fast_macd = int(dbconf.get('Indicator', 'period_fast_macd'))#12
    period_slow_macd = int(dbconf.get('Indicator', 'period_slow_macd'))#26
    signal_macd =  int(dbconf.get('Indicator', 'signal_macd'))   #9
    period_fast_ao = int(dbconf.get('Indicator', 'period_fast_ao')) #5
    period_slow_ao = int(dbconf.get('Indicator', 'period_slow_ao')) #34
    period_uo1 = int(dbconf.get('Indicator', 'period_uo1'))     #7
    period_uo2 = int(dbconf.get('Indicator', 'period_uo2'))     #14
    period_uo3 = int(dbconf.get('Indicator', 'period_uo3'))     #28





    # ADX Indicator
    adx = tafin.trend.ADXIndicator(
        df['high'], df['low'], df['close'], period_adx)
    #df['ADX'] =round(tafin.trend.ADXIndicator.adx(adx),6)
    df['ADX'] = tafin.trend.ADXIndicator.adx(adx)
    #df['minus'] =round(tafin.trend.ADXIndicator.adx_neg(adx),4)
    #df['plus'] =round(tafin.trend.ADXIndicator.adx_pos(adx),4)
    df['minus'] =tafin.trend.ADXIndicator.adx_neg(adx)
    df['plus'] =tafin.trend.ADXIndicator.adx_pos(adx)
    #print("ADX: ", df['ADX'].iloc[-1])
    #print("ADXM: ", df['minus'].iloc[-1])
    #print("ADXP: ", df['plus'].iloc[-1])



    # EMAs 9-12-26-100
    #df['EMA9'] = TA.EMA(df, 9)
    df['EMA'] = round(TA.EMA(df, period_ema),8)
    #df['EMA12'] = TA.EMA(df, 12)
    #df['EMA26'] = TA.EMA(df, 26)

    # MACD
    df['MACD'] =TA.MACD(df, period_fast_macd, period_slow_macd, signal_macd)['MACD']
    #print("MACD: ",df['MACD'].iloc[-1])
    df['MACD_signal'] = TA.MACD(df, period_fast_macd, period_slow_macd, signal_macd)['SIGNAL']
    #print("MACD_signal: ",df['MACD_signal'].iloc[-1])


    #AO
    ao = tafin.momentum.AwesomeOscillatorIndicator(df['high'],df['low'],period_fast_ao,period_slow_ao)
    df['AO'] = tafin.momentum.AwesomeOscillatorIndicator.awesome_oscillator(ao)
    #print("AO: ",df['AO'].iloc[-1])
    #RSI

    #rsi = tafin.momentum.RSIIndicator(df['close'],14)
    #df['RSI'] = round(tafin.momentum.RSIIndicator.rsi(rsi),8)

    #UO

    uo = tafin.momentum.UltimateOscillator(df['high'],df['low'],df['close'],period_uo1,period_uo2,period_uo3,4,2,1)
    df['UO'] = round(tafin.momentum.UltimateOscillator.ultimate_oscillator(uo),8)


    return df

def data_news(CAS):
    headers = requests.utils.default_headers()
    headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"})
    input_language = 'TH'
    currencys = [CAS]
    data_web = requests.get(f"http://th.investing.com/economic-calendar/", headers=headers)
    data_news = []
    data_news_currency = []
    data_if_currency = []
    if data_web.status_code == requests.codes.ok:
        info = bts(data_web.text, "html.parser")
        data_find = ((info.find("table", {"id": "economicCalendarData"})).find("tbody")).findAll("tr", {"class": "js-event-item"})
        for data_finds in data_find:
            star = str((data_finds.find("td", {"class": "sentiment"})).get("data-img_key")).replace("bull", "")
            date = str(data_finds.get("data-event-datetime")).replace("/", "-")
            currency = (data_finds.find("td", {"class": "left flagCur noWrap"})).text.strip()
            detail = (data_finds.find("td", {"class": "left event"})).text.strip()
            date_if = str(data_finds.get("data-event-datetime")).replace(":", "").replace("/", "").replace(" ", "")
            data_news.append({"currency": currency, "date": date, "star": star, "detail": detail, "date_if": int(date_if[8:12])})
        for data_news_i in data_news:
            if data_news_i["currency"] == currencys[0]:
                data_news_currency.append(data_news_i)
        if len(data_news_currency) != 0:
            return data_news_currency
        else:
            return None



def login(IQ_api, balance_mode):
    """
    Logs in to the broker.

    Requires IQ object and balance mode (default PRACTICE)
    """

    Email = dbconf.get('Login', 'Email')
    Pass = dbconf.get('Login', 'Pass')
    try:
        iq = IQ_api(Email, Pass)
        check, reason = iq.connect()
        if check:
            print('Logged in...')
            print('Balance mode:', balance_mode)
            iq.change_balance(balance_mode)
            print(f"Balance : {iq.get_balance()} {iq.get_currency()}")
    except:
        print('Failed to login')
    return iq

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

def exp():
    root = Tk()
    w = Label(root, font="50")
    w.pack()



    r = requests.get('http://just-the-time.appspot.com/')
    utc_current_time = datetime.datetime.strptime(r.content.decode().strip(), '%Y-%m-%d %H:%M:%S')
    #print(f'utc_current_time: {utc_current_time}')
    utc_offset_in_seconds = time.timezone
    if (utc_offset_in_seconds > 0):
        local_time = utc_current_time - datetime.timedelta(seconds=abs(time.timezone))
    else:
        local_time = utc_current_time + datetime.timedelta(seconds=abs(time.timezone))
    #print(f'local_time: {local_time}')

    exp = datetime.datetime(2022, 7, 11)
    timeBK = local_time
    currentBK = timeBK.strftime("%Y-%m-%d")
    start_date = datetime.datetime.strptime(currentBK, "%Y-%m-%d")
    sum = exp - start_date
    sumexp = strfdelta(sum, '{D} Days')
    if start_date >= exp:
        root.withdraw()
        messagebox.showerror("Error", "Your tool had expired")
        exit()
    else:
        print("Bot will Expire :", sumexp)
        pass


