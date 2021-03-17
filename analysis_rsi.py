from model.rsi import *
from data.function import getData
import pandas as pd

TSLA_data = getData(t="TSLA")

# 篩選2019年開收盤價資料
Close = TSLA_data["Close"]
Open = TSLA_data["Open"]

# 參數最佳化 No1，所有參數皆可調整
max_total_ret, max_period, max_upper, max_lower = 0, 0, 0, 0
for period in range(5,10):
    for upper in range(67,84):
        for lower in range(16,33):
            ret = RSI_backtest(RSI_Trading_Sig(RSI(Close, period), upper, lower), Open)
            if ret > max_total_ret:
                max_total_ret, max_period, max_upper, max_lower = ret, period, upper, lower

# 將求出來的結果印出參數及圖看看
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import gridspec

x = RSI(Close, max_period).index
y = RSI(Close, max_period).values

fig = plt.figure(figsize=(15,10))
# set height ratios for sublots
gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 

# the fisrt subplot
ax0 = plt.subplot(gs[0])
# line0 = ax0.plot(x, y, color='r')
ax0.plot(RSI(Close, max_period))
ax0.axhline(y=max_upper, color='red')
ax0.axhline(y=max_lower, color='green')

#the second subplot
# shared axis X
ax1 = plt.subplot(gs[1], sharex = ax0)
rsi_sig = pd.Series(index = RSI(Close, max_period).index, data = list(RSI_Trading_Sig(RSI(Close, max_period), max_upper, max_lower).values))
ax1.plot(rsi_sig)
for i, r in enumerate(rsi_sig):
    if r == 1:
        print(rsi_sig.index[i], "SELL, Price: ", TSLA_data.loc[rsi_sig.index[i]]['Close'])
    if r == -1:
        print(rsi_sig.index[i], "BUY, Price: ", TSLA_data.loc[rsi_sig.index[i]]['Open'])
print('總報酬率：' + str(round(100*(max_total_ret-1),2)) + '%')
print('參數：' + 'RSI計算天數: ' + str(max_period) + ' ,Upper bond: ' + str(max_upper) + ' ,Lower bond: ' + str(max_lower))
plt.show()