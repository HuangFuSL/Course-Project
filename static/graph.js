function get_data(type) {
    url = '/api/graph_' + type.toString();

    console.log(sessionStorage.getItem('criteria'))

    var ret;
    $.ajax({
        url: url,
        async: false,
        type: "POST",
        data: sessionStorage.getItem('criteria'),
        dataType: 'json',
        headers: { 'Access-Control-Allow-Origin': '*' },
        contentType: "application/json",
        xhrFields: { withCredentials: false },
        crossDomain: true,
        success: function (res) {
            ret = res.data;
        }
    });

    return ret
}

function pie_chart(title, series) {
    return {
        title: { text: title, left: 'center' },
        legend: { left: 'center', top: 'bottom' },
        series: [
            {
                type: 'pie',
                radius: [20, 140],
                roseType: 'radius',
                itemStyle: { borderRadius: 5 },
                label: { show: false },
                emphasis: { label: { show: true } },
                data: series
            }
        ]
    }
}

function bar_plot(title, x_series, y_series) {
    return {
        title: { text: title, left: 'center' },
        xAxis: { type: 'category', data: x_series },
        yAxis: { type: 'value' },
        series: [{
            type: 'bar', barWidth: '60%', data: y_series
        }]
    };
}

function group_by(array, f) {
    let groups = {};
    array.forEach(function (o) {
        let group = JSON.stringify(f(o));
        groups[group] = groups[group] || [];
        groups[group].push(o);
    });
    return Object.keys(groups).map(function (group) {
        return groups[group];
    });
}

function floor_by(base, field) {
    return function (item) {
        return Math.floor(item[field] / base) * base;
    }
}

function fill(x, y, step) {
    var x_ret = [], y_ret = [];
    for (let i in x) {
        if (!i)
            continue;
        if (x[i] - x[i - 1] > step)
        {
            for (let j = x[i - 1] + step; j < x[i]; j += step)
            {
                x_ret.push(j);
                y_ret.push(0);
            }
        }

        x_ret.push(x[i]);
        y_ret.push(y[i]);
    }

    return [x_ret, y_ret];
}

function make_data(type) {
    var data = get_data(type), option = {};

    switch (type) {
        case 1:
            var x = [], y = [];
            for (i in data) {
                x.push(data[i].date);
                y.push(data[i].price)
            }
            option = {
                xAxis: { type: 'category', data: x },
                yAxis: { type: 'value' },
                series: [{ data: y, type: 'line' }]
            };
            break;

        case 2:
            var series = [], i;
            for (i in data)
                series.push({ name: data[i].city, value: data[i].count });
            option = pie_chart('数量-城市分布图', series);
            break;

        case 3:
            var x = [], y = [];
            for (i in data) {
                x.push(data[i].city);
                y.push(data[i].price)
            }
            option = bar_plot('价格-城市分布图', x, y);
            break;

        case 4:
            var series = [], i;
            for (i in data)
                series.push({ name: data[i].district, value: data[i].count });
            option = pie_chart('数量-区划分布图', series);
            break;

        case 5:
            var x = [], y = [];
            for (i in data) {
                x.push(data[i].district);
                y.push(data[i].price)
            }
            option = bar_plot('价格-区划分布图', x, y);
            break;

        case 8:
            var x = [], y = [];
            for (i in data) {
                if (data[i].construct_time)
                    x.push(data[i].construct_time);
                y.push(data[i].count);
            }
            option = bar_plot('数量-楼龄分布图', x, y);
            break;

        case 9:
            var x = [], y = [];
            for (i in data) {
                if (data[i].construct_time)
                    x.push(data[i].construct_time);
                y.push(data[i].price);
            }
            option = bar_plot('价格-楼龄分布图', x, y);
            break;

        case 10:
            var grouper = floor_by(10, 'outer_square')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            for (let i in grouped) {
                var square = 0, sum = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].count;
                }
                x.push(square);
                y.push(sum);
            }

            temp = fill(x, y, 10);
            x = temp[0];
            y = temp[1];

            option = bar_plot('数量-面积分布图', x, y);
            break;

    }

    return option;
}