#! /usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
from tornado.httpserver import HTTPServer
import json
from queue import Queue
from urllib.request import urlopen
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from base64 import b64decode
import re

qlogin = Queue()
qBuy = Queue()

'''
'''
def unionId(m):
    wxspAppid = "wxe42429b73e0dc401"
    wxspSecret = "597083cbe2f0852aad632ed24186a1b8"
    code = m["code"]
    iv = b64decode(m["iv"])
    encryptedData = b64decode(m["encryptedData"]) 
    grant_type = "authorization_code"
    params = "appid=" + wxspAppid + "&secret=" + wxspSecret + "&js_code=" + code + "&grant_type=" + grant_type
    url = "https://api.weixin.qq.com/sns/jscode2session?" + params
    sr = urlopen(url).read()
    sr = json.loads(str(sr,"utf-8"))
    session_key = b64decode(sr["session_key"])
    openid = sr["openid"]
    aes = AES.new(session_key, AES.MODE_CBC, iv)
    r = str(aes.decrypt(encryptedData),"utf-8")
    r = re.match("{.+}",r).group()
    f = open('tst','w')
    print(r,file=f)
    r = json.loads(r)
    unionId = r["unionId"]
    return unionId


'''
@云端跟微信端会话
'''
class cloud_and_client(tornado.websocket.WebSocketHandler):
    user_request = dict()
    def open(self):
        pass

    def on_message(self,message):
        message = json.loads(message)
        uID = unionId(message)

    def on_close(self):
        print("{id} is closed".format(id = id(self)))

    def check_origin(self,origin):
        return True

'''
@云端跟本地服务端会话
'''
class cloud_and_local(tornado.websocket.WebSocketHandler):
    def open(self):
        print("local is connected!")
        pass

    def on_message(self,message):
        pass

    def on_close(self):
        print("{id} is closed".format(id = id(self)))

    def check_origin(self,origin):
        return True



def main():
    print("tornado start.")
    app = tornado.web.Application([
        (r'/',cloud_and_client),
        (r'/cloud_and_local',cloud_and_local),
        ])
    server = HTTPServer(app,ssl_options={"certfile":"1_luozhiming.club_bundle.crt","keyfile":"2_luozhiming.club.key"})
    server.listen(443)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == "__main__":
    main()
