import pandas as pd
import numpy as np
import math

def movingAverage(data, days):
    return data.loc["close"][-days:].mean()

def movingAverageIndicator(data, days, actions):
    movingAverages = [movingAverage(data, day) for day in days]
    MA_diffs = [movingAverages[i] - movingAverages[i + 1] for i in range(len(movingAverages) - 1)]
    action = 0
    if (MA_diffs[0] > MA_diffs[1]) * (MA_diffs[1] > MA_diffs[2]):
        action = 1
    elif (MA_diffs[0] > MA_diffs[1]):
        action = actions[0]
    elif (MA_diffs[1] > MA_diffs[2]):
        action = actions[1]
    else:
        action = -1
    return action

def calRSV(data):
    RSV = (data.loc["close"][-1] - min(data.loc["low"][-9:])) / (max(data.loc["high"][-9:]) - min(data.loc["low"][-9:])) * 100
    return RSV

def KDIndicator(data, days, KD_upbound, KD_lowbound, keepDays):
    alpha = 0.333
    K_list, D_list = [0.5], [0.5]
    for i in range(days):
        RSV = calRSV(data.iloc[:, :-days + i])
        K_new = (1 - alpha) * K_list[-1] + alpha * RSV
        D_new = (1 - alpha) * D_list[-1] + alpha * K_new
        K_list.append(K_new)
        D_list.append(D_new)

    K_list, D_list = K_list[1:], D_list[1:]
    K, D = K_list[-1], D_list[-1]
    KD_diffCounts = sum(np.array(K_list) - np.array(D_list) > 0)
    
    action = 0
    if K > D:
        action = 1
    elif K < D < KD_lowbound:
        action = -1 if KD_diffCounts < keepDays else 1
    elif K > D > KD_upbound:
        action = 1 if KD_diffCounts > keepDays else -1
    elif K < D:
        action = -1
    return action

def calRSI(data, days):
    rise, fall = 0, 0
    riseOrFall = np.array(data.loc["close"][-days:] - data.loc["open"][-days:])
    rise = sum(riseOrFall[riseOrFall > 0])
    fall = sum(riseOrFall[riseOrFall < 0])
    SMAu = rise / days
    SMAd = fall / days
    return SMAu / (SMAu + SMAd) * 100

def RSIIndicator(data, RSI_upbound, RSI_lowbound, long, short, cross_w, RSI_w, threshold):
    action = 0
    short_RSI = calRSI(data, short)
    long_RSI = calRSI(data, long)

    high_level = 1 if short_RSI > long_RSI >= RSI_upbound else 0
    low_level = 1 if RSI_lowbound >= long_RSI > short_RSI else 0

    cross = (1 if short_RSI > long_RSI else 0) - (1 if long_RSI > short_RSI else 0)
    RSI = low_level - high_level
    indicator = cross_w * cross + RSI_w * RSI
    # print('RSI indicator: ', indicator)
    action = 1 if indicator > threshold else -1
    return action

def calEMA(data, days):
    EMA = movingAverage(data, days)
    for i in range(days):
        EMA = (EMA * (days - 1) + data.loc["close"][-1] * 2) / (days + 1)
    return EMA

def calDIF(short_EMA, long_EMA):
    return short_EMA - long_EMA

def calIndicator(DIF, MACD):
    value = np.array(DIF) - np.array(MACD)
    indicator = math.exp(value[-1])
    return indicator

def MACDIndicator(data, long, short, days, threshold):
    DIF_list, MACD_list = [], [0.5]
    for i in range(days):
        short_EMA = calEMA(data.iloc[:, :-days + i], short)
        long_EMA = calEMA(data.iloc[:, :-days + i], long)
        DIF = calDIF(short_EMA, long_EMA)
        DIF_list.append(DIF)
        MACD_new = (MACD_list[-1] * (days - 1) + DIF * 2) / (days + 1)
        MACD_list.append(MACD_new)
    MACD_list = MACD_list[1:]
    indicator = calIndicator(DIF_list, MACD_list)
    # print('MACD indicator: ', indicator)
    action = 1 if indicator > threshold else -1
    return action

if __name__ == '__main__':
    datapath = '../data/prunedData/0050'
    data = pd.read_csv(datapath, index_col = 0)
    # print(data)
    print(
            # movingAverageIndicator(data, [5, 10, 20, 40], [1, -1]),
            KDIndicator(data, 5, 80, 20, 3),
            # RSIIndicator(data, 80, 20, 20, 5, 0.5, 0.5, 0.5),
            # MACDIndicator(data, 26, 12, 9, 0.5),
         )
    