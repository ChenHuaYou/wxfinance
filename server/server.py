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
from goto import with_goto
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import traceback
from retry import retry

sched = BlockingScheduler()
conn = pymongo.MongoClient()
db = conn.server

chunk_list = lambda a_list, n: zip_longest(*[iter(a_list)]*n)
all_stocks = sorted(tushare.get_stock_basics().index.tolist())



def send_on_message(ws, message):
    pass

def send_ts_on_message(ws,data):
    req = json.loads(data)
    code = req['msg']
    msg = db.market.find_one({'code':code},{"code":1,"market":1})
    msg = {msg["code"]:msg["market"]}
    print(msg)
    data = {"from_id":-2,"from_group":"server","to_id":req["from_id"],"to_group":
    "client","msg":msg,"func":"send_ts"}
    ws.send(json.dumps(data))

def send_kl_on_message(ws,data):
    req = json.loads(data)
    code = req['msg']
    msg = db.kl.find_one({'code':code},{"code":1,"kl":1})
    msg = {msg["code"]:msg["kl"]}
    print(msg)
    data = {"from_id":-3,"from_group":"server","to_id":req["from_id"],"to_group":
    "client","msg":msg,"func":"send_kl"}
    ws.send(json.dumps(data))

def recv_on_message(ws, data):
    req = json.loads(data)["msg"]
    exec(req)


def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def send_zxg_on_open(ws):
    print("### send zxg opened ###")
    data = {"from_id":-1,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_zxg_on_open"}
    ws.send(json.dumps(data))
    send_zxg(ws)

def send_ts_on_open(ws):
    print("### send ts opened ###")
    data = {"from_id":-2,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_ts_on_open"}
    ws.send(json.dumps(data))

def send_kl_on_open(ws):
    print("### send kl opened ###")
    data = {"from_id":-3,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_kl_on_open"}
    ws.send(json.dumps(data))

def send_market_on_open(ws):
    print("### send market opened ###")
    data = {"from_id":-4,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"send_market_on_open"}
    ws.send(json.dumps(data))
    send_market(ws)


def recv_on_open(ws):
    print("### recv opened ###")
    data = {"from_id":2,"from_group":"server","to_id":0,"to_group":
    "server","msg":"","func":"recv_on_open"}
    ws.send(json.dumps(data))



#这里发送自选股到微信端
@retry()
def send_zxg(ws):
    def get_market(code_list_str):
        url = "http://hq.sinajs.cn/list={codes}".format(codes = code_list_str)
        hq = urlopen(url).read().decode('gbk')
        return hq

    while True:
        curs = db.user.find({},{"unionId":1,"zxg":1})
        data = "" 
        stocks = list(map(lambda x: "sh"+x if x[0]=="6" else "sz"+x, all_stocks))
        stocks = list(chunk_list(stocks, 100))
        stocks = list(map(lambda x: [j for j in x if j != None], stocks))
        stocks = list(map(lambda x: ",".join(x), stocks))
        with ThreadPool(30) as pool:
            return_list = pool.map(get_market,stocks)
            pool.close()
            pool.join()
        for i in return_list:
            data = data + str(i)
        data = data.split(";")
        market = dict()
        for i in data:
            code = re.search('hq_str_\w{2}(\d{6})',i)
            value = re.search('="(.+),00"',i)
            if not (code and value):
               continue 
            code = code.group(1)
            value = value.group(1).split(',')
            market.update({code:value})
        for j in curs:
            msg = {k:v for k,v in market.items() if k in j["zxg"]}
            data = {"from_id":-1,"from_group":"server","to_id":j["unionId"],"to_group":"client","msg":msg, "func":"send_zxg"} 
            ws.send(json.dumps(data))

#这里不停的广播实时价格行情
@retry()
def send_market(ws):
    def get_market(code_list_str):
        url = "http://hq.sinajs.cn/list={codes}".format(codes = code_list_str)
        hq = urlopen(url).read().decode('gbk')
        return hq

    while True:
        curs = db.user.find({},{"unionId":1,"zxg":1})
        data = "" 
        stocks = list(map(lambda x: "sh"+x if x[0]=="6" else "sz"+x, all_stocks))
        stocks = list(chunk_list(stocks, 100))
        stocks = list(map(lambda x: [j for j in x if j != None], stocks))
        stocks = list(map(lambda x: ",".join(x), stocks))
        with ThreadPool(30) as pool:
            return_list = pool.map(get_market,stocks)
            pool.close()
            pool.join()
        for i in return_list:
            data = data + str(i)
        data = data.split(";")
        market = dict()
        for i in data:
            code = re.search('hq_str_\w{2}(\d{6})',i)
            value = re.search('="(.+),00"',i)
            if not (code and value):
               continue 
            code = code.group(1)
            value = value.group(1).split(',')
            market.update({code:value})

        msg = market 
        data = {"from_id":-4,"from_group":"server","to_id":"all","to_group":"client","msg":msg, "func":"send_market"} 
        ws.send(json.dumps(data))

#这里每天准时5点正读取收盘价序列
def get_tushare_kl():
    print("...","send kl")
    for code in all_stocks:
        DF = tushare.get_hist_data(code)
        if DF is not None and len(DF):
            DF = DF.reset_index()
            value = DF.values.tolist()
            db.kl.update({'code':code},{'$setOnInsert':{'code':code},'$set':{'kl':value}},upsert=True)

#这里马不停蹄的读取新浪行情保存到数据库
def get_sina_ts():
    def get_market(code_list_str):
        url = "http://hq.sinajs.cn/list={codes}".format(codes = code_list_str)
        hq = urlopen(url).read().decode('gbk')
        return hq

    db.market.drop()    
    while True:
        print("...send ts")
        T = datetime.datetime.now()
        if T.hour == 15:
            return

        st = time.time()
        data = "" 
        stocks = list(map(lambda x: "sh"+x if x[0]=="6" else "sz"+x, all_stocks))
        stocks = list(chunk_list(stocks, 100))
        stocks = list(map(lambda x: [j for j in x if j != None], stocks))
        stocks = list(map(lambda x: ",".join(x), stocks))
        with ThreadPool(30) as pool:
            return_list = pool.map(get_market,stocks)
            pool.close()
            pool.join()
        for i in return_list:
            data = data + str(i)
        data = data.split(";")

        for i in data:
            code = re.search('hq_str_\w{2}(\d{6})',i)
            value = re.search('="(.+),00"',i)
            if not (code and value):
                continue
            code = code.group(1)
            value = value.group(1).split(',')
            db.market.update({'code':code},{'$setOnInsert':{'code':code},'$addToSet':{'market':value}},upsert=True)


def server_send_zxg():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_zxg_on_open
                                )
    ws.run_forever()

def server_send_market():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_market_on_open
                                )
    ws.run_forever()


def server_send_ts():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_ts_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_ts_on_open
                                )
    ws.run_forever()


def server_send_kl():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_kl_on_message,
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

def get_data():
    sched.add_job(get_tushare_kl,'cron',day_of_week='mon-fri',hour='5')
    sched.add_job(get_sina_ts,'cron',day_of_week='mon-fri',hour='9',minute='15')
    sched.start()


def main():
    with Pool(10) as p:
        p.apply_async(get_data,())
        p.apply_async(server_recv,())
        p.apply_async(server_send_zxg,())
        p.apply_async(server_send_ts,())
        p.apply_async(server_send_kl,())
        p.apply_async(server_send_market,())
        p.close()
        p.join()
if __name__ == "__main__":
    main()
