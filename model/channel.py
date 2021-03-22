import backtrader as bt
import math
from datetime import date, timedelta, datetime
from tools.tools import prev_weekday
from var.channel_var import *

# 定義一個Indicator物件
class DonchianChannels(bt.Indicator):
    # 這個物件的別名，所以後面我們可以用DCH/DonchianChannel來呼叫這個指標
    alias = ('DCH', 'DonchianChannel',)
    
    # 三條線分別代表唐奇安通道中的 中軌(上軌加下軌再除以2)、上軌、下軌
    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low
    
    # 軌道的計算方式：用過去20天的資料來計算，所以period是20，lookback的意思是要不要將今天的資料納入計算，由於唐奇安通道是取過去20天的最高或最低，所以一定不能涵蓋今天，不然永遠不會有訊號出現，所以要填-1(從前一天開始算20天)
    # 計算前 20 日的高點
    params = dict(
        period=PERIOD,
        lookback=LOOKBACK,  # consider current bar or not
    )
    
    # 是否要將Indicators另外畫一張圖，然而通道線通常都是跟股價圖畫在同一張，才能看得出相對關係，所以這裡就填subplot=False
    plotinfo = dict(subplot=False)  # plot along with data
    
    # 繪圖設定，ls是line style，'--'代表虛線
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )
    
    def __init__(self):
        # hi與lo是指每日股價的最高與最低價格
        hi, lo = self.data.high, self.data.low

        # 視需求決定是否要從前一天開始讀資料，上面已經定義lookback存在，所以這邊會直接從前一天的資料開始跑
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)
        
        # 定義三條線的計算方式
        self.l.dch = bt.ind.Highest(hi, period=self.p.period)
        self.l.dcl = bt.ind.Lowest(lo, period=self.p.period)
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0  # avg of the above

# 撰寫交易策略
class MyStrategy(bt.Strategy):

    # 交易紀錄
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.counter_buy = 0
        self.counter_sell = 0
        # DCH就是上面定義的 DonchianChannels的alias
        self.myind = DCH()
        self.setsizer(sizer())
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.datachigh = self.datas[0].high
        self.dataclow = self.datas[0].low


    def next(self):
        if self.data[0] < self.myind.dcl[0]:
            self.log('BUY ' + ', Price: ' + str(self.dataopen[0]))
            self.buy(price=self.dataopen[0])
            self.counter_sell = 0
        elif self.data[0] > self.myind.dch[0]:
            self.counter_sell += 1
            if self.counter_sell > SELL_TIMES:
                self.log('SELL ' + ', Price: ' + str(self.dataclose[0]))
                # for data in self.datas:
                #     size=self.getposition(data).size
                #     if  size!= 0:
                #         self.close(data)
                self.sell(price=self.dataclose[0])
                self.counter_sell = 0

class sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            if data.datetime.date(0) == prev_weekday(datetime.today().date()):
                print("BUY today!")
                return math.floor(self.broker.getposition(data).size)
            return math.floor(cash/data[1]/BUY_SIZE)
        else:
            # return self.broker.getposition(data)
            if data.datetime.date(0) == prev_weekday(datetime.today().date()):
                print("SELL today!")
                return math.floor(self.broker.getposition(data).size)
            return math.floor(self.broker.getposition(data).size/SELL_SIZE)
