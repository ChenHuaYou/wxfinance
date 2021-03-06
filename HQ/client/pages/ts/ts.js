/**
 * Created by ChenChao on 2016/9/27.
 */

var app = getApp();
var storage = require('../../utils/storage');
var TS = require('../../utils/wxChart/time-sharing');
var axisShow = require('../../utils/wxChart/axis-show');
var ts1, ts2;     //分时
var tsd51, tsd52; //五日
var tsAxisShow;   //分时手势坐标
var getOptionTimeSharing1 = function (type, width) {
  return {
    name: type || 'time-sharing',
    width: 'auto',
    height: '200',
    axis: {
      row: 4,
      col: 4,
      paddingTop: 0,
      paddingBottom: 0,
      paddingLeft: 0,
      paddingRight: 0,
      color: '#cdcdcd'
    },
    xAxis: {
      data: []
    },
    yAxis: [
      {
        type: 'line',
        lineColor: '#2F6098',
        background: 'rgba(53,125,222,0.1)',
        /*background: function () {  //渐变背景在IOS上会影响均线颜色，这个应该是小程序canvas的bug
            return ['rgba(53,125,222,0.3)', 'rgba(0,0,0,0)'];
        },*/
        data: []
      },
      {
        type: 'line',
        lineColor: '#A96F3E',
        data: []
      }
    ],
    callback: function (time) {
      var page = getCurrentPages();
      page = page[page.length - 1];
      page.setData({
        ts1RenderTime: time
      });
    }
  };
};
var getOptionTimeSharing2 = function (type, width) {
  return {
    name: type || 'time-sharing-b',
    width: width || 'auto',
    height: 80,
    axis: {
      row: 2,
      col: 4,
      showEdg: true,
      showX: true,
      showY: true,
      paddingTop: 5,
      paddingBottom: 14,
      paddingLeft: 0,
      paddingRight: 0,
      color: '#cdcdcd'
    },
    xAxis: {
      times: ['09:30', '15:00'],
      data: []
    },
    yAxis: [
      {
        type: 'bar',
        color: [],
        data: [],
        showMax: true
      }
    ],
    callback: function (time) {
      var page = getCurrentPages();
      page = page[page.length - 1];
      page.setData({
        ts2RenderTime: time
      });
    }
  };
};
var getOptionTimeSharingAxis = function () {
  return {

  };
};
var timer = null;

Page({
  data: {
    tabName: '',
    ts: {},
    ts5: {},
    stock: '',
    code: '',
    time: '',
    yc: '',
    now_price: '',
    dataIndex: 0,
    ts1RenderTime: 0,
    ts2RenderTime: 0,
    timerIndex: 4,
    timerArray: ['50ms', '100ms', '200ms', '500ms', '1000ms'],
    isShowAxis: false
  },
  onReady: function () {
    this.interval = setInterval(this.fresh_market,1000);
  },
  fresh_market: function () {
    var that = this;
    var code = that.data.code;
    var ts = app.Data.ts;
    var unionId = app.Data.unionId;
    var req = code;
    console.log(ts[code].length);
    wx.sendSocketMessage({
      data: JSON.stringify({ "from_id": unionId, "from_group": "client", "to_id": -2, "to_group": "server", "msg": req }),
      success: function () { console.log("请求分时图"); }
    });
    try {
      ts = ts[code];
      var mdata;
      var price = new Array();
      var L = ts.length;
      var avg = 0;
      var sum = 0;
      var j = 0;
      for (var i = 0; i < L; i++) {
        var s_now = (ts[i][30] + ' ' + ts[i][31]).replace(/-/g, "/");
        var s_open = (ts[i][30] + ' ' + '09:30:00').replace(/-/g, "/");
        var date_now = new Date(s_now);
        var date_open = new Date(s_open);
        if (date_now < date_open) continue;
        j ++;
        sum =  parseFloat(ts[i][3]) + sum;
        avg = String(sum / j);
        console.log("avg",avg);
        var p = '{date} {time},{price},{vol},{avg_price},0'.format({ 'date': ts[L-1][30], 'time': ts[i][31], 'price': ts[i][3], 'vol': ts[i][9], 'avg_price': avg});
        price.push(p);
      }
      mdata = { 'open': ts[L-1][1], 'yc': ts[L-1][2], 'price': price, 'highest': ts[L-1][4], 'lowest': ts[L-1][5]};
      var tsData = storage.getTsData(mdata);
      this.setData({
        dataIndex: 0,
        time: '{date} {time}'.format({ 'date': ts[L-1][30], 'time': ts[L-1][31]}),
        ts: tsData,
        yc: ts[L-1][2],
        now_price: ts[L-1][3],
      });
      that.tabChart({
        target: {
          dataset: {
            type: 'ts'
          }
        }
      });
      //clearInterval(that.interval);
    }catch(err){
      console.log(err);
    }

  },

  onLoad: function (options) {
    this.setData({
      stock: options.stock,
      code: options.code
    });
    var unionId = app.Data.unionId;
    var req = options.code;
    wx.sendSocketMessage({
      data: JSON.stringify({ "from_id": unionId, "from_group": "client", "to_id": -2, "to_group": "server", "msg": req }),
      success: function () { console.log("请求分时图"); }
    });

  },
  onUnload: function () {
    clearInterval(this.interval);
  },
  onHide: function () {
    clearInterval(timer);
  },
  klChart: function () {
    console.log("klChart fuck");
    var that = this;
    wx.redirectTo({
      url: '../kl/kl?stock={stock}&code={code}'.format({ "stock": that.data.stock, "code": that.data.code }),
    });
  },
  back: function () {
    wx.redirectTo({
      url: '../zxg/zxg',
    })
  },
  tabChart: function (e) {
    //this.clearTimer();
    var type = e.target.dataset.type;
    var data = this.data[type];
    this.setData({
      tabName: type,
    });
    this['init-ts']();
  },
  'init-ts': function () {
    var data = this.data.ts;
    ts1 = TS('time-sharing').init(getOptionTimeSharing1());
    this.renderTs1(data);
    ts2 = TS('time-sharing-b').init(getOptionTimeSharing2());
    this.renderTs2(data);
    tsAxisShow = axisShow('time-sharing-axis', {
      //todo: 配置项
      type: 'ts',
      height: 280,
      width: 1440,
      maxY: 100,
      minY: 0
    });
    tsAxisShow.init();
  },
  'init-ts5': function () {
    var data = this.data.ts5;
    tsd51 = ts('time-sharing-5day').init(getOptionTimeSharing1('time-sharing-5day'));
    tsd52 = ts('time-sharing-5day-b').init(getOptionTimeSharing2('time-sharing-5day'));
    tsd51.metaData1(data, getOptionTimeSharing1('time-sharing-5day'));
    tsd51.draw();
    tsd52.metaData2(data, getOptionTimeSharing2('time-sharing-5day'));
    tsd52.draw();
  },
  renderTs1: function (data) {
    ts1.metaData1(data, getOptionTimeSharing1());
    ts1.draw();
  },
  renderTs2: function (data) {
    ts2.metaData2(data, getOptionTimeSharing2());
    ts2.draw();
  },
  clearTimer: function () {
    clearInterval(timer);
    this.setData({
      dataIndex: 0
    });
  },
  reset: function () {
    this.clearTimer();

    var data = storage.getTsData();
    console.log("fuck me !!");
    this.renderTs1(data);
    this.renderTs2(data);
  },
  dynamic: function () {
    var that = this;
    var data = storage.getTsData();
    console.log("fuck you !!")
    var origin = data.data.slice(0);
    var index = 0;
    var times = [50, 100, 200, 500, 1000];
    clearInterval(timer);
    timer = setInterval(function () {
      index += 1;
      if (index > 241 + 16) {
        clearInterval(timer);
        return;
      }
      data.data = origin.slice(0, index);
      that.renderTs1(data);
      that.renderTs2(data);
      that.setData({
        dataIndex: index
      });
    }, times[this.data.timerIndex]);
  },
  bindTimeChange: function (e) {
    var index = e.detail.value;
    this.setData({
      timerIndex: index === '' ? 4 : index
    });
    this.dynamic();
  },
  axisStart: function (e) {
    var x = e.touches[0].x;
    var y = e.touches[0].y;
    this.data.isShowAxis = true;
    tsAxisShow.start(x, y);
  },
  axisMove: function (e) {
    if (this.data.isShowAxis) {
      var x = e.touches[0].x;
      var y = e.touches[0].y;
      tsAxisShow.move(x, y);
    }
  },
  axisStop: function () {
    this.data.isShowAxis = false;
    tsAxisShow.stop();
  }
});
