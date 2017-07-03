#! /usr/bin/python3
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.autoreload
from tornado.httpserver import HTTPServer
import json
from queue import Queue

qlogin = Queue()
qBuy = Queue()

'''
'''
def unionId(m):
    print(m)
    pass


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
