// pages/index/ZXG.js
var app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    market: [
      { "code": "000001", "name": "上证指数", "price": 0, "pct_chg": -0.22 },
    ],

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

    console.log("fuck you !!!!!!!!!!!!!!!!!!")
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    this.interval = setInterval(this.fresh_market, 1000);
  },
  fresh_market: function () {
    var that = this;
    var gmarket = app.Data.market;
    console.log("fuck the on ready!")
    var market = new Array();
    for (var code in gmarket) {
      var name = gmarket[code][0];
      var price = gmarket[code][3];
      var pct_chg = 100*(gmarket[code][3] - gmarket[code][2])/gmarket[code][2];
      pct_chg = pct_chg.toFixed(2); 
      market.push({"code":code,"name":name,"price":price,"pct_chg":pct_chg}); 
    }
    console.log(market);
    that.setData({
      market: market,
    })
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

  }
})

