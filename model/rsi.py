def RSI(Close, period=12):
    # 整理資料
    import pandas as pd
    Chg = Close - Close.shift(1)
    Chg_pos = pd.Series(index=Chg.index, data=Chg[Chg>0])
    Chg_pos = Chg_pos.fillna(0)
    Chg_neg = pd.Series(index=Chg.index, data=-Chg[Chg<0])
    Chg_neg = Chg_neg.fillna(0)
    # 計算12日平均漲跌幅度
    import numpy as np
    up_mean = []
    down_mean = []
    for i in range(period+1, len(Chg_pos)+1):
        up_mean.append(np.mean(Chg_pos.values[i-period:i]))
        down_mean.append(np.mean(Chg_neg.values[i-period:i]))
    # 計算 RSI
    rsi = []
    for i in range(len(up_mean)):
        rsi.append( 100 * up_mean[i] / ( up_mean[i] + down_mean[i] ) )
    rsi_series = pd.Series(index = Close.index[period:], data = rsi)
    return rsi_series

def RSI_Trading_Sig(RSI, upper = 80, lower = 20):
    import pandas as pd
    # 訊號標籤
    sig = []
    # 庫存標籤，只會是0或1，表示每次交易都是買進或賣出所有部位
    stock = 0
    # 偵測RSI訊號
    for i in range(len(RSI)):
        if RSI[i] > upper and stock == 1:
            stock -= 1
            sig.append(-1)
        elif RSI[i] < lower and stock == 0:
            stock += 1
            sig.append(1)
        else:
            sig.append(0)
    # 將格式轉成 time series
    rsi_sig = pd.Series(index = RSI.index, data = sig)
    return rsi_sig

def RSI_backtest(RSI_Trading_Sig, Open_Price):
    # 每次買賣的報酬率
    rets = []
    # 是否仍有庫存
    stock = 0
    # 當次交易買入價格
    buy_price = 0
    # 當次交易賣出價格
    sell_price = 0
    # 每次買賣的報酬率
    for i in range(len(RSI_Trading_Sig)-1):
        if RSI_Trading_Sig[i] == 1:
            # 隔日開盤買入
            buy_price = Open_Price[RSI_Trading_Sig.index[i+1]]
            stock += 1
        elif RSI_Trading_Sig[i] == -1:
            # 隔日開盤賣出
            sell_price = Open_Price[RSI_Trading_Sig.index[i+1]]
            stock -= 1
            rets.append((sell_price-buy_price)/buy_price)
            buy_price = 0
            sell_price = 0
    # 如果最後手上有庫存，就用回測區間最後一天的開盤價賣掉
    if stock == 1 and buy_price != 0 and sell_price == 0:
        sell_price = Open_Price[-1]
        rets.append((sell_price-buy_price)/buy_price)
    # 總報酬率
    total_ret = 1
    for ret in rets:
        total_ret *= 1 + ret
    return total_ret