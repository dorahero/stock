import backtrader as bt
from model.channel import MyStrategy
from datetime import datetime
from data.function import getData
import matplotlib.pyplot as plt
from pylab import rcParams

rcParams['figure.figsize'] = 16,9
rcParams['figure.facecolor'] = '#eeeeee'
plt.title('dummy')
plt.plot([1,3,2,4])
plt.close()

cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
cerebro.broker.setcash(3000)
cerebro.broker.setcommission(commission=0.001)

# data = bt.feeds.YahooFinanceData(dataname='TSLA',
#                                  fromdate=datetime(2020, 1, 1),
#                                  todate=datetime(2020, 9, 15))

df = getData(t='AMZN')

data = bt.feeds.PandasData(dataname=df)

cerebro.adddata(data)
print('Starting Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()
print('Ending Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()