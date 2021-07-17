function clear_table() {
    var i = 0;
    for (i = document.getElementById("tbMain").rows.length; i > 1; i--) {
        document.getElementById("tbMain").deleteRow(1);
    }
}

function reset_table() {
    window.offset = 0;
    window.limit = 20;
    clear_table();
}

function query(offset, limit) {
    var d = new Date();
    d.setTime(d.getTime() + 24 * 60 * 60 * 1000);

    var info = $("#filter").serializeArray(), allInfo = {};
    for (var i = 0; i < info.length; i++)
        if (info[i].value != "")
            allInfo[info[i].name] = info[i].value;

    if (allInfo.lat && allInfo.lng) {
        allInfo.location = {
            lng: allInfo.lng,
            lat: allInfo.lat,
            dist: allInfo.dist
        }
    }

    var requestBody = {};
    if (offset === undefined)
        window.offset = 0;
    else
        window.offset = offset + 20;
    if (limit === undefined)
        window.limit = 20;
    requestBody.criteria = allInfo;
    requestBody.offset = window.offset;
    requestBody.limit = window.limit;

    $.ajax({
        url: "/api/retrieval/",
        data: JSON.stringify(requestBody),
        type: "POST",
        headers: { 'Access-Control-Allow-Origin': '*' },
        contentType: "application/json",
        async: false,
        xhrFields: { withCredentials: false },
        crossDomain: true,
        success: function (res) {
            clear_table();
            for (i = 0; i < res.data.length; i++) {
                var houseURL = 'https://bj.ke.com/ershoufang/' + res.data[i].beike_ID + '.html';
                var title = res.data[i].title;
                var totalPrice = res.data[i].anon_1;
                var unitPrice = res.data[i].price_per_square;
                var distance = res.data[i].distance;
                var layout = res.data[i].bedroom + '室' + res.data[i].bathroom + '卫' + res.data[i].living_room + '厅';
                var floor = '';

                switch (res.data[i].floor_no)
                {
                    case 0:
                        floor = "高楼层";
                        break;
                    case 1:
                        floor = "中楼层";
                        break;
                    case 2:
                        floor = "低楼层";
                        break;
                    case 3:
                        floor = "底层";
                        break;
                    case 4:
                        floor = "顶层";
                        break;
                    case 5:
                        floor = "地下室";
                        break;
                    default:
                        floor = "暂无数据"
                }

                var square = res.data[i].outer_square, decoration = '';
                switch (res.data[i].decoration) {
                    case 0:
                        decoration = '精装';
                        break;
                    case 1:
                        decoration = '简装';
                        break;
                    case 2:
                        decoration = '其他';
                        break;
                    case 3:
                        decoration = '毛坯';
                        break;
                }

                var row = '<tr onclick="window.open(\'' + houseURL + '\');"><td>' + title + '</td><td>' + Math.floor(totalPrice) + '</td><td>' + unitPrice + '</td><td>' + distance + '</td><td>' + layout + '</td><td>' + floor + '</td><td>' + '</td><td>' + '</td><td>' + square + '</td><td>' + decoration + '</td></tr>';

                document.getElementById('tbMain').innerHTML += row;
                document.getElementById('tbMain').hidden = false;
                document.getElementById('btPane').hidden = false;
            }
        },
        fail: function (err) {
            console.log(err)
            alert('fail');
        }
    });
}