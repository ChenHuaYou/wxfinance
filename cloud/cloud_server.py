#! /usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
from tornado.httpserver import HTTPServer
from tornado.options import options, define
import json
from queue import Queue
from urllib.request import urlopen
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from base64 import b64decode
import re
import pymongo
import traceback

user = dict()
define("port",default=443,help="跑在443",type=int)


def unionId(m):
    '''
    @获取客户的unionId
    '''
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
    r = json.loads(r)
    unionId = r["unionId"]
    return unionId

class cloud_route(tornado.websocket.WebSocketHandler):
    """
    @云端作为信息路由
    @信息格式:{"from_id":发送端id,"from_group":发送端组,"to_id":接收端id,"to_group":接受端组,"msg":信息}
    @组可以分为: client, server 
    @client由unionId区分
    @server由1,2,3,...区分
    @目前规定:1发送数据,2接受请求
    """

    def route(self,data):
        print("...",data["to_id"])
        try:
            if data["to_id"] == 0:
                self.login(data)
            elif data["to_id"] == "all":
                for k,v in user.items():
                    if k not in [2,0,-1,-2,-3,-4,-5]:
                        v.write_message(data)
            elif data["to_id"] == 2:
                user[2].write_message(data)
            else:
                user[data["to_id"]].write_message(data)
        except:
            traceback.print_exc()

    def login(self,data):
        try:
            if data["from_id"] == "None":
                unionID = unionId(data["msg"]) 
                user.update({unionID:self})
                data = {"from_id":0,"from_group":"server","to_id":unionID,"to_group":"client","msg":unionID,"func":"login"}
                self.write_message(json.dumps(data))
            else:
                user.update({data["from_id"]:self})
            print(user)
        except:
            traceback.print_exc()

    def open(self):
        pass

    def on_message(self,data):
        data = json.loads(data)
        self.route(data)

    def on_close(self):
        _id = {v:k for k,v in user.items()}[self]
        user.pop(_id)
        print("{Id} is closed".format(Id=_id))

    def check_origin(self,origin):
        return True


def main():
    print("tornado start.")
    app = tornado.web.Application([
        (r'/',cloud_route),
        ],
        debug = False)
    server = HTTPServer(app,ssl_options={"certfile":"1_luozhiming.club_bundle.crt","keyfile":"2_luozhiming.club.key"})
    server.bind(options.port)
    server.start(0)
    tornado.ioloop.IOLoop.instance().start()
  

if __name__ == "__main__":
    main()
