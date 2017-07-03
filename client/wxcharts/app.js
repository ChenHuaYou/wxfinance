/**
 * Created by ChenChao on 2017/1/12.
 */

App({
    onLaunch: function () {
        //调用API从本地缓存中获取数据
        var logs = wx.getStorageSync('logs') || [];
        logs.unshift(Date.now());
        wx.setStorageSync('logs', logs);
        wx.login({
          success:function(r){
            var code = r.code;
            if(code){
              wx.getUserInfo({
                success:function(res){
                  var msg = { 'encryptedData': res.encryptedData, 'iv': res.iv, 'code': code };
                  msg = JSON.stringify(msg);
                  wx.connectSocket({
                    url: 'wss://luozhiming.club',
                    success:function(res){   
                      wx.onSocketOpen(function(){
                        wx.sendSocketMessage({
                          data: msg,
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
    onShow: function () {
        //todo
    },
    onHide: function () {
        //todo
    },
    getUserInfo: function (cb) {
        var that = this;
        if (this.globalData.userInfo) {
            typeof cb == "function" && cb(this.globalData.userInfo)
        } else {
            //调用登录接口
            wx.login({
                success: function () {
                    wx.getUserInfo({
                        success: function (res) {
                            that.globalData.userInfo = res.userInfo;
                            typeof cb == "function" && cb(that.globalData.userInfo)
                        }
                    })
                }
            });
        }
    },
    globalData: {
        userInfo: null
    }
});
