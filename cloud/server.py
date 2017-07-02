#! /usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
from tornado.httpserver import HTTPServer
import pandas as pd
import json


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    cols = ["id","user","request"]
    user_request = pd.DataFrame(columns = cols) 
    def open(self):
        self.request = {"id":id(self),"user":self,"request":None}
        self.write_message("hello client!")

    def on_message(self,message):
        self.request["request"]=message
        WebSocketHandler.user_request=WebSocketHandler.user_request.append(self.request,ignore_index=True)
        print("client sent message:")
        print(WebSocketHandler.user_request)

    def on_close(self):
        WebSocketHandler.user_request = WebSocketHandler.user_request[WebSocketHandler.user_request["id"] != id(self)]

    def check_origin(self,origin):
        return True

def main():
    print("tornado start.")
    app = tornado.web.Application([
        (r'/',WebSocketHandler),
        ])
    server = HTTPServer(app,ssl_options={"certfile":"1_luozhiming.club_bundle.crt","keyfile":"2_luozhiming.club.key"})
    server.listen(443)
    instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(instance)
    instance.start()

if __name__ == "__main__":
    main()
