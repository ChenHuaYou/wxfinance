module.exports = {
  user_login: user_login,
  user_send: user_send
}

function login_cloud() {
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
                    data: JSON.stringify({"from_id":"None","from_group":"client","to_id":0,"to_group":"server","msg":msg}),
                  })
                  wx.onSocketMessage(function (res) {
                    console.log(res.data);
                  })
                })
              }
            })
          }
        })
      }
    }
  })
}

function user_send(msg) {
  wx.sendSocketMessage({
    data: msg,
  })
}

