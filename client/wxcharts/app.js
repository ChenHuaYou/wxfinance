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
    this.user_login();
    console.log(wx.getStorageSync("unionId"));
  },
  onShow: function () {

    //todo
  },
  onHide: function () {
    //todo
  },
  user_login: function () {
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
                      data: JSON.stringify({ "from_id": "None", "from_group": "client", "to_id": 0, "to_group": "server", "msg": msg }),
                    })
                    wx.onSocketMessage(function (res) {
                      var unionId = res.data
                      wx.setStorageSync('unionId', unionId);
                      var req = ("db.user.update({'unionId':'{unionId1}'}," +
                        "{'$setOnInsert':{'unionId':'{unionId2}'},'$addToSet':{'zxg':{'$each':['000001','399006']}}},upsert=True)").format({ "unionId1": unionId, "unionId2": unionId });
                      wx.sendSocketMessage({
                        data: JSON.stringify({ "from_id": unionId, "from_group": "client", "to_id": 2, "to_group": "server", "msg": req }),
                      })
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
  globalData: {
    unionID: "",
  }
});
