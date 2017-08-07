// pages/sr/sr.js
var app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    code: '',
    stock: '',

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.setData({
      code: options.code,
    });

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    //this.interval = setInterval(this.fresh_market, 1000);
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {
    clearInterval(this.interval);
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },
  /**
   * 跳转到行情
   */
  go_to_ts: function (event) {
    var code = event.currentTarget.dataset.id;
    var stock = event.currentTarget.dataset.name;
    console.log(code);
    console.log(stock);
    wx.redirectTo({
      url: '../ts/ts?stock={stock}&code={code}'.format({ "stock": stock, "code": code }),
    });
    console.log("hello zxg!");
  },
  /**
   * 添加自选股
   */
  addround: function (event) {
    var that = this;
    console.log("!!!clicked");
    var unionId = app.Data.unionId;
    var code = event.currentTarget.dataset.id;
    console.log(unionId);
    console.log(code);
    var req = ("db.user.update({'unionId':'{unionId1}'}," +
      "{'$addToSet':{'zxg':'{code}'}})").format({ "unionId1": unionId,"code":code});
    console.log(req);
    wx.sendSocketMessage({
      data: JSON.stringify({ "from_id": unionId, "from_group": "client", "to_id": 2, "to_group": "server", "msg": req }),
      success:function() {console.log("添加自选代码")}
    });
    wx.redirectTo({
      url: '../index/ZXG',
    })
  }
})

