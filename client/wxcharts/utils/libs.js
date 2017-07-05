module.exports = {
  user_login: user_login,
  user_send: user_send
}

function user_login() {
  wx.login({
    success: function (r) {
      var code = r.code;
      if (code) {
        wx.getUserInfo({
          success: function (res) {
            var msg = { 'encryptedData': res.encryptedData, 'iv': res.iv, 'code': code };
            msg = JSON.stringify(msg);
            wx.connectSocket({
              url: 'wss://luozhiming.club',
              success: function (res) {
                wx.onSocketOpen(function () {
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
}

function user_send(msg) {
  wx.sendSocketMessage({
    data: msg,
  })
}