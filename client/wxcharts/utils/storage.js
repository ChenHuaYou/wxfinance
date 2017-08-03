/**
 * Created by ChenChao on 2017/1/16.
 * demo 用的数据
 */

module.exports = {
    getTsData: function (mdata) {
        return {
            "name": "测试数据",
            "code": "100000",
            "info": {
                "c": "15.99",
                "h": mdata['highest'],
                "l": mdata['lowest'],
                "o": mdata['open'],
                "a": "1146574928",
                "v": "730574",
                "yc": mdata['yc'],
                "time": "2017-01-17 15:00:00",
                "ticks": "34200|54000|1|34200|41400|46800|54000",
                "total": "241",
                "pricedigit": "0.00"
            },
            "data": mdata['price']
        };
    },
    
    getDkData: function (price) {
        return {
            "name": "测试数据",
            "code": "100000",
            "info": {
                "c": "15.82",
                "h": "15.84",
                "l": "15.75",
                "o": "15.80",
                "a": "24561144",
                "v": "15543",
                "yc": "15.99",
                "time": "2017-01-18 09:32:34",
                "ticks": "34200|54000|0|34200|41400|46800|54000",
                "total": "1598",
                "pricedigit": "0.00"
            },
            "data": price
        };
    }
};