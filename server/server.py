#! /usr/bin/python3

import websocket
import time
import json
from multiprocessing import Pool
import builtins
import pymongo 

conn = pymongo.MongoClient()
db = conn.server



def send_on_message(ws, message):
    pass

def recv_on_message(ws, req):
    global db
    print(req)
    exec(req)


def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")


def send_on_open(ws):
    print("### send opened ###")
    data = {"from_id":1,"from_group":"server","to_id":0,"to_group":
    "server","msg":""}
    ws.send(json.dumps(data))
    send_loop()

def recv_on_open(ws):
    print("### recv opened ###")
    data = {"from_id":2,"from_group":"server","to_id":0,"to_group":
    "server","msg":""}
    ws.send(json.dumps(data))

def send_loop():
    with Pool(4) as p:
        p.async_apply(send_market,(,))
    p.close()
    p.join()        

def send


def send():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://luozhiming.club/",
                                on_message = send_on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_open = send_on_open
                                )
    ws.run_forever()

def recv():
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
        p.apply_async(send,())
        p.apply_async(recv,())
        p.close()
        p.join()
if __name__ == "__main__":
    main()
