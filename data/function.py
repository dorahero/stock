import pandas as pd

def getData(t='TSLA'):
    from sqlalchemy import create_engine
    from util.setting import MYSQL_URL
    engine = create_engine(MYSQL_URL)

    # inspector = inspect(engine)
    # schemas = inspector.get_schema_names()
    # table_list = []

    data_col = ['Close','High','Low','Open','Volume']
    # for schema in schemas:
    #     if schema == "stock":
    #         for table_name in inspector.get_table_names(schema=schema):
    #             table_list.append(table_name)
    df = pd.read_sql(t, engine, index_col=['date'], columns=['Close','High','Low','Open','Volume'])
    print(f"Get data {t} !")
    return df

# 串接API取資料
import os
import pandas_datareader as pdr

import requests
import pandas as pd

def updateData():
    from sqlalchemy import create_engine, inspect
    from util.setting import MYSQL_URL
    engine = create_engine(MYSQL_URL)

    inspector = inspect(engine)
    schemas = inspector.get_schema_names()

    table_list = []
    data_col = ['Close','High','Low','Open','Volume']
    for schema in schemas:
        if schema == "stock":
            for table_name in inspector.get_table_names(schema=schema):
                table_list.append(table_name)

    from util.setting import TOKEN
    from datetime import date

    today = date.today()
    # 貼上連結
    url = 'https://www.slickcharts.com/sp500'
    headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

    request = requests.get(url, headers = headers)

    data = pd.read_html(request.text)[0]
    data.head(10)
    # 欄位『Symbol』就是股票代碼
    stk_list = data.Symbol

    # 用 replace 將符號進行替換
    stk_list = data.Symbol.apply(lambda x: x.replace('.', '-'))

    for s in stk_list[:10]:
        TSLA = pdr.get_data_tiingo(s, api_key=TOKEN)
        TSLA = TSLA.reset_index(level=[0,1])

        TSLA.index = TSLA['date']
        TSLA_adj = TSLA.iloc[:,7:12]
        TSLA_adj.columns = ['Close','High','Low','Open','Volume']

        TSLA_adj = TSLA_adj[(TSLA_adj.index > '2020-01-01') & (TSLA_adj.index < today.strftime("%Y-%m-%d"))]

        if s in table_list:
            TSLA_adj.to_sql(s, engine, if_exists='replace')
        print(s, "Insert successfully")