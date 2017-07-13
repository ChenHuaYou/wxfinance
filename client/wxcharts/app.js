/**
 * Created by ChenChao on 2017/1/12.
 */

require("utils/lib.js")

App({
  onLaunch: function () {
    //调用API从本地缓存中获取数据
    var logs = wx.getStorageSync('logs') || [];
    logs.unshift(Date.now());
    wx.setStorageSync('logs', logs);
  },
  onShow: function () {
    var that = this;
    console.log("on show");
    that.user_login();
    that.MessageHandler();
  },
  onHide: function () {
    //todo
  },
  user_login: function () {
    console.log("user login~")
    wx.login({
      success: function (r) {
        var code = r.code;
        if (code) {
          wx.getUserInfo({
            success: function (res) {
              var msg = { 'encryptedData': res.encryptedData, 'iv': res.iv, 'code': code };
              wx.connectSocket({
                url: 'wss://luozhiming.club',
                success: function (res) {
                  wx.onSocketOpen(function () {
                    wx.sendSocketMessage({
                      data: JSON.stringify({ "from_id": "None", "from_group": "client", "to_id": 0, "to_group": "server", "msg": msg, "func": "user_login" }),
                    })
                  })
                }
              })
            }
          })
        }
      }
    })
  },
  MessageHandler: function () {
    var that = this;
    console.log("message handler~")
    wx.onSocketMessage(function (res) {
      var data = JSON.parse(res.data)
      if (data["from_id"] == 0 && data["func"] == "login") {
        var unionId = data["msg"];
        that.Data.unionId = unionId;
        var req = ("db.user.update({'unionId':'{unionId1}'}," +
          "{'$setOnInsert':{'unionId':'{unionId2}'},'$addToSet':{'zxg':{'$each':['000001','399006']}}},upsert=True)").format({ "unionId1": unionId, "unionId2": unionId });
        wx.sendSocketMessage({
          data: JSON.stringify({ "from_id": unionId, "from_group": "client", "to_id": 2, "to_group": "server", "msg": req }),
        })
      }else if (data["from_id"]==1 && data["func"] == "send_market") {
          var market = data["msg"];
          that.Data.market = market; 
      }
    })
  },
  Data: {
    unionId: null,
    market: null,
  }
});
