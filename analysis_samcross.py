import backtrader as bt
from model.samcross import SmaCross
from datetime import datetime
from data.function import getData
import matplotlib.pyplot as plt
from pylab import rcParams

rcParams['figure.figsize'] = 16,9
rcParams['figure.facecolor'] = '#eeeeee'
plt.title('dummy')
plt.plot([1,3,2,4])
plt.close()

df = getData(t='TSLA')

data = bt.feeds.PandasData(dataname=df)

# 初始化cerebro
cerebro = bt.Cerebro()
cerebro.broker.setcash(10000)
cerebro.broker.setcommission(commission=0.0005)
# feed data
cerebro.adddata(data)
# add strategy
cerebro.addstrategy(SmaCross)
# run backtest
print('Starting Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Ending Value: %.2f' % cerebro.broker.getvalue())
# plot diagram
cerebro.plot()