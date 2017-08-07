// pages/index/ZXG.js
var WxSearch = require('../../wxSearch/wxSearch.js')
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
	var that = this
	WxSearch.init(that,43,['000001','000002']);
	WxSearch.initMindKeys(['000001','000002']);
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
    var market = new Array();
    for (var code in gmarket) {
      var lstmarket = gmarket[code];
      lstmarket = lstmarket[lstmarket.length-1];
      var name = lstmarket[0];
      var price = lstmarket[3];
      var pct_chg = 100 * (lstmarket[3] - lstmarket[2]) / lstmarket[2];
      pct_chg = pct_chg.toFixed(2);
      market.push({ "code": code, "name": name, "price": price, "pct_chg": pct_chg });
    }
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

  },
  /**
   * 跳转到自选股行情
   */
  go_to_ts: function (event) {
    var code = event.currentTarget.dataset.id;
    var stock = event.currentTarget.dataset.name;
    console.log(code);
    console.log(stock);
	wx.redirectTo({
      url: '../ts/ts?stock={stock}&code={code}'.format({"stock":stock,"code":code}),
    });
    console.log("hello zxg!");
  },
  /**
   * 添加自选股
   */
  addround: function(event) {
    console.log("!!!clicked")
  },  
  wxSearchFn: function(e){
    var that = this
    WxSearch.wxSearchAddHisKey(that);
	var code = that.data.wxSearchData.value;
    if(typeof(code) == "undefined" || code.length == 0){return;}
	console.log(code);
	wx.redirectTo({
      url: '../sr/sr?code={code}'.format({"code":code}),
    });	
  },
  wxSearchInput: function(e){
    var that = this
    WxSearch.wxSearchInput(e,that);
  },
  wxSerchFocus: function(e){
    var that = this
    WxSearch.wxSearchFocus(e,that);
  },
  wxSearchBlur: function(e){
    var that = this
    WxSearch.wxSearchBlur(e,that);
  },
  wxSearchKeyTap:function(e){
    var that = this
    WxSearch.wxSearchKeyTap(e,that);
  },
  wxSearchDeleteKey: function(e){
    var that = this
    WxSearch.wxSearchDeleteKey(e,that);
  },
  wxSearchDeleteAll: function(e){
    var that = this;
    WxSearch.wxSearchDeleteAll(that);
  },
  wxSearchTap: function(e){
    var that = this
    WxSearch.wxSearchHiddenPancel(that);
  }
})

