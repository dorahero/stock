import requests
import pandas as pd
from datetime import datetime

from sqlalchemy import create_engine, inspect
from util.setting import MYSQL_URL
engine = create_engine(MYSQL_URL)

inspector = inspect(engine)
schemas = inspector.get_schema_names()

table_list = ["ARKK", "NFLX", "NVDA", "TTWO", "VOO"]
data_col = ['Close','High','Low','Open','Volume']
for schema in schemas:
    if schema == "stock":
        for table_name in inspector.get_table_names(schema=schema):
            table_list.append(table_name)
# print(table_list)
for t in table_list:
    df = pd.DataFrame(columns=data_col)
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?region=US&lang=en-US&includePrePost=false&interval=5m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance'
    headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

    res = requests.get(url, headers = headers)
    _ = {}
    ans = res.json()
    _['date'] = datetime.utcnow()
    _['Close'] = ans['chart']['result'][0]['meta']['regularMarketPrice']
    _['High'] = max(ans['chart']['result'][0]['indicators']['quote'][0]['high'])
    _['Low'] = min(ans['chart']['result'][0]['indicators']['quote'][0]['low'])
    _['Open'] = ans['chart']['result'][0]['indicators']['quote'][0]['open'][0]
    _['Volume'] = sum(ans['chart']['result'][0]['indicators']['quote'][0]['volume'])
    df = df.append(_, ignore_index=True)
    df.set_index('date',inplace=True)
    df.to_sql(t, engine, if_exists='append')
    print(t, " updated!")