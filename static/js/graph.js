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
        if (x[i] - x[i - 1] > step) {
            for (let j = x[i - 1] + step; j < x[i]; j += step) {
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
                y.push(data[i].sum / data[i].count)
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
                series.push({ name: data[i].city, value: data[i].sum });
            option = pie_chart('??????-???????????????', series);
            break;

        case 3:
            var x = [], y = [];
            for (i in data) {
                x.push(data[i].city);
                y.push(data[i].sum / data[i].count)
            }
            option = bar_plot('??????-???????????????', x, y);
            break;

        case 4:
            var series = [], i;
            for (i in data)
                series.push({ name: data[i].district, value: data[i].sum });
            option = pie_chart('??????-???????????????', series);
            break;

        case 5:
            var x = [], y = [];
            for (i in data) {
                x.push(data[i].district);
                y.push(data[i].sum / data[i].count)
            }
            option = bar_plot('??????-???????????????', x, y);
            break;
        
        case 6:
            var grouper = floor_by(100, 'distance')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            console.log(grouped)

            for (let i in grouped) {
                var square = 0, sum = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                }
                x.push(square);
                y.push(sum);
            }

            temp = fill(x, y, 100);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-?????????????????????', x, y);
            break;
        
        case 7:
            var grouper = floor_by(100, 'distance')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            console.log(grouped)

            for (let i in grouped) {
                var square = 0, sum = 0, count = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                    count += grouped[i][j].count;
                }
                x.push(square);
                y.push(sum / count);
            }

            temp = fill(x, y, 100);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-?????????????????????', x, y);
            break;

        case 8:
            var grouper = floor_by(5, 'construct_time')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            console.log(grouped)

            for (let i in grouped) {
                var square = 0, sum = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                }
                x.push(square);
                y.push(sum);
            }

            temp = fill(x, y, 5);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-???????????????', x, y);
            break;

        case 9:
            var grouper = floor_by(5, 'construct_time')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            console.log(grouped)

            for (let i in grouped) {
                var square = 0, sum = 0, count = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                    count += grouped[i][j].count;
                }
                x.push(square);
                y.push(sum / count);
            }

            temp = fill(x, y, 5);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-???????????????', x, y);
            break;

        case 10:
            var grouper = floor_by(10, 'outer_square')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            for (let i in grouped) {
                var square = 0, sum = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                }
                x.push(square);
                y.push(sum);
            }

            temp = fill(x, y, 10);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-???????????????', x, y);
            break;

        case 11:
            var grouper = floor_by(10, 'outer_square')
            var grouped = group_by(data, grouper);
            var x = [], y = [], temp;

            for (let i in grouped) {
                var square = 0, sum = 0, count = 0;
                for (let j in grouped[i]) {
                    square = grouper(grouped[i][j]);
                    sum += grouped[i][j].sum;
                    count += grouped[i][j].count;
                }
                x.push(square);
                y.push(sum / count);
            }

            temp = fill(x, y, 10);
            x = temp[0];
            y = temp[1];

            option = bar_plot('??????-???????????????', x, y);
            break;
        
        case 12:
            
    }

    return option;
}