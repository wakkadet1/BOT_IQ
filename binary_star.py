from scipy.special import logsumexp

# TODO:
# some way to calculate direction of the trend to open position in that direction only.

def ema_cross(df):
    """
    Verifies if emas crossed each other
    """

    ema9_1 = df['EMA9'].iloc[-1]
    ema12_1 = df['EMA12'].iloc[-1]
    ema26_1 = df['EMA26'].iloc[-1]
    ema9_2 = df['EMA9'].iloc[-2]
    ema12_2 = df['EMA12'].iloc[-2]
    ema26_2 = df['EMA26'].iloc[-2]
    ema9_3 = df['EMA9'].iloc[-3]
    ema12_3 = df['EMA12'].iloc[-3]
    ema26_3 = df['EMA26'].iloc[-3]

    if (ema9_1 > ema12_1 and ema9_1 > ema26_1) and (
            (ema9_2 < ema12_2 and ema9_2 < ema26_2) or (ema9_3 < ema12_3 and ema9_3 < ema26_3)):
        return 1
    elif (ema9_1 < ema12_1 and ema9_1 < ema26_1) and (
            (ema9_2 > ema12_2 and ema9_2 > ema26_2) or (ema9_3 > ema12_3 and ema9_3 > ema26_3)):
        return -1
    else:
        return 0

def ema(df):

    if df['close'].iloc[-1] > df['EMA'].iloc[-1]:
        return 1
    elif df['close'].iloc[-1] < df['EMA'].iloc[-1]:
        return -1
    else:
        return 0

def adx_cross(df):
    """
    Verifies if ADX signals crossed each other
    """

    plus_1 = logsumexp(df['plus'].iloc[-1])
    minus_1 = logsumexp(df['minus'].iloc[-1])
    adx_1 = logsumexp(df['ADX'].iloc[-1]+5)

#    if plus_1 > minus_1 and plus_1 > adx_1:
#        return 1
#    elif minus_1 > plus_1 and minus_1 > adx_1:
#        return -1
#    else:
#        return 0

#    if plus_1 > minus_1 and adx_1 > 23 and plus_1 > adx_1:
#        return 1
#    elif minus_1 > plus_1 and adx_1 > 23 and minus_1 > adx_1:
#        return -1
#    else:
#        return 0
    if plus_1 > minus_1 and plus_1 > adx_1 and adx_1 > 25:
        return 1
    elif minus_1 > plus_1 and minus_1 > adx_1 and adx_1 >25:
        return -1
    else:
        return 0

def macd_cross(df):
    """
    Verifies if MACD crossed 0
    """


#    if df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1] and df['MACD'].iloc[-2] < df['MACD_signal'].iloc[-2]:
#        return 1
#    elif df['MACD'].iloc[-1] < df['MACD_signal'].iloc[-1] and df['MACD'].iloc[-2] > df['MACD_signal'].iloc[-2]:
#        return -1
#    else:
#        return 0
    if logsumexp(df['MACD'].iloc[-1]) > logsumexp(df['MACD_signal'].iloc[-1]):
        #print("MACD: ",df['MACD'].iloc[-1])
        return 1
    elif logsumexp(df['MACD'].iloc[-1]) < logsumexp(df['MACD_signal'].iloc[-1]):
        #print("MACD: " ,df['MACD'].iloc[-1])
        return -1
    else:
        return 0


def AO(df):

    #if df['AO'].iloc[-2] < 0 and df['AO'].iloc[-1] > 0:
    #    return  1
    #elif df['AO'].iloc[-2] > 0 and df['AO'].iloc[-1] < 0 :
    #    return  -1
    #else:
    #    return  0

    if logsumexp(df['AO'].iloc[-1]) > 0:
        #print("AO: " ,df['AO'].iloc[-1])
        return  1
    elif logsumexp(df['AO'].iloc[-1]) < 0 :
        #print("AO: " ,df['AO'].iloc[-1])
        return  -1
    else:
        return  0
def RSI(df):

    if df['RSI'].iloc[-1] > 50:
        return  1
    elif df['RSI'].iloc[-1] < 50 :
        return  -1
    else:
        return  0

def UO(df):

    if df['UO'].iloc[-1] > 50 and df['UO'].iloc[-1] <= 70 :
        return  1
    elif df['UO'].iloc[-1] < 50 and df['UO'].iloc[-1] >= 30 :
        return  -1
    else:
        return  0





