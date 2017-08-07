#! /usr/bin/python3

import websocket
import time
import json
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import builtins
import pymongo 
import os
import tushare
from urllib.request import urlopen
from itertools import zip_longest
from queue import Queue
import pandas as pd
import re
import sys
import datetime

conn = pymongo.MongoClient()
db = conn.server

chunk_list = lambda a_list, n: zip_longest(*[iter(a_list)]*n)
all_stocks = sorted(tushare.get_stock_basics().index.tolist())



def send_on_message(ws, message):
    pass

def recv_on_message(ws, data):
    print("recv:",data)
    req = json.loads(data)["msg"]
    exec(req)


def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")


def send_ts_on_open(ws):
    print("### send opened ###")
    data = {"from_id":1,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_on_open"}
    send_market(ws)

def send_kl_on_open(ws):
    print("### send opened ###")
    data = {"from_id":1,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_on_open"}
    send_kl(ws)


def recv_on_open(ws):
    print("### recv opened ###")
    data = {"from_id":2,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"recv_on_open"}
    ws.send(json.dumps(data))


def get_market(code_list_str):
    url = "http://hq.sinajs.cn/list={codes}".format(codes = code_list_str)
    hq = urlopen(url).read().decode('gbk')
    return hq

def send_kl(ws):
    T = datetime.datetime.now()
    for code in all_stocks:
        print(code)
        record = db.kl.find_one({'code':code},{'Date':1})
        print(record)
        if record and record['Date'].day == T.day:
            continue
        DF = tushare.get_hist_data(code)
        if DF is not None and len(DF):
            DF = DF.reset_index()
            value = DF.values.tolist()
            db.kl.update({'code':code},{'$setOnInsert':{'code':code},'$set':{'kl':value,'Date':T}},upsert=True)
    print("kl ... done")
    while True:
        curs = db.user.find({},{"unionId":1,"zxg":1})
        kl = dict([(d['code'],d['kl']) for d in list(db.kl.find({},{'code':1,'kl':1}))])
        print("...kl")
        for j in curs:
            stock=j["zxg"]
            msg = {key:value for key,value in kl.items() if key in stock}
            data = {"from_id":1,"from_group":"server","to_id":j["unionId"],"to_group":"client","msg":msg, "func":"send_kl"} 
            print(json.dumps(data))
            ws.send(json.dumps(data))

def send_market(ws):
    T = time.localtime()
    if T.tm_hour * 60 + T.tm_min <= 9*60 + 30:
        db.market.drop()    
    while True:
        st = time.time()
        data = "" 
        stocks = list(map(lambda x: "sh"+x if x[0]=="6" else "sz"+x, all_stocks))
        stocks = list(chunk_list(stocks, 100))
        stocks = list(map(lambda x: [j for j in x if j != None], stocks))
        stocks = list(map(lambda x: ",".join(x), stocks))
        pool = ThreadPool(30)
        return_list = pool.map(get_market,stocks)
        pool.close()
        pool.join()
        for i in return_list:
            data = data + str(i)
        data = data.split(";")
        market=dict()
        for i in data:
            code = re.search('hq_str_\w{2}(\d{6})',i)
            value = re.search('="(.+),00"',i)
            if not (code and value):
                continue
            code = code.group(1)
            value = value.group(1).split(',')
            db.market.update({'code':code},{'$setOnInsert':{'code':code},'$addToSet':{'market':value}},upsert=True)
        curs = db.user.find({},{"unionId":1,"zxg":1})
        market = dict([(d['code'],d['market']) for d in list(db.market.find({},{'code':1,'market':1}))])
        for j in curs:
            stock=j["zxg"]
            msg = {key:value for key,value in market.items() if key in stock}
            data = {"from_id":1,"from_group":"server","to_id":j["unionId"],"to_group":"client","msg":msg, "func":"send_market"} 
            ws.send(json.dumps(data))


def server_send_ts():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_ts_on_open
                                )
    ws.run_forever()


def server_send_kl():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_kl_on_open
                                )
    ws.run_forever()


def server_recv():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = recv_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = recv_on_open
                                )
    ws.run_forever()


def main():
    with Pool(2) as p:
        p.apply_async(server_send_ts,())
        p.apply_async(server_send_kl,())
        p.apply_async(server_recv,())
        p.close()
        p.join()
if __name__ == "__main__":
    main()
