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


    if (allInfo.city === undefined) {
        alert("请输入城市");
        return;
    }

    sessionStorage.setItem('criteria', JSON.stringify(allInfo));

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

                switch (res.data[i].floor_no) {
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

function setCity() {
    window.map = new BMapGL.Map('allMap');
    window.map.centerAndZoom(new BMapGL.Point(110, 33), 5);

    window.map.enableScrollWheelZoom(true);
    window.map.addControl(new BMapGL.ScaleControl());
    window.map.addControl(new BMapGL.ZoomControl());

    window.map.addEventListener("click", function (e) {
        var pt = e.latlng;
        window.map.centerAndZoom(pt, 15);
        window.map.clearOverlays();
        window.map.addOverlay(new BMapGL.Marker(pt));

        document.getElementById("longitude").value = pt.lng;
        document.getElementById("latitude").value = pt.lat;
        document.getElementById("dist").options[1].selected = "selected";
    });

    window.arrBJ = new Array('', '东城', '西城', '朝阳', '丰台', '石景山', '海淀', '门头沟', '房山', '通州', '顺义', '昌平', '大兴', '怀柔', '平谷', '密云', '延庆');
    window.arrSH = new Array('', '黄浦', '徐汇', '长宁', '静安', '普陀', '虹口', '杨浦', '闵行', '宝山', '嘉定', '浦东新', '金山', '松江', '青浦', '奉贤', '崇明');
    window.arrGZ = new Array('', '荔湾', '越秀', '海珠', '天河', '白云', '黄埔', '番禺', '花都', '南沙', '从化', '增城');
    window.arrSZ = new Array('', '罗湖', '福田', '南山', '宝安', '龙岗', '盐田', '龙华', '坪山', '光明');
    window.arrAll = new Array('', window.arrBJ, window.arrSH, window.arrGZ, window.arrSZ);
}

function setArea() {
    var cityNum = parseInt(document.getElementById("city").selectedIndex, 10);
    document.getElementById("area").length = 0;
    if (cityNum) {
        var i = 0;
        for (i = 0; i < window.arrAll[cityNum].length; i++) {
            var tempOp = document.createElement('option');
            tempOp.value = window.arrAll[cityNum][i];
            tempOp.text = window.arrAll[cityNum][i];
            if (i == 0) {
                tempOp.selected = "true";
            }
            document.getElementById("area").appendChild(tempOp);
        }
    }

    switch (cityNum) {
        case 0: {
            var tempPt = new BMapGL.Point(110, 33);
            window.map.centerAndZoom(tempPt, 5);
            document.body.style.backgroundImage = "url('/img/background.png')";
            break;
        }
        case 1: {
            var tempPt = new BMapGL.Point(116.40351686607113, 39.923722008555245);
            window.map.centerAndZoom(tempPt, 12);
            document.body.style.backgroundImage = "url('/img/beijing.png')";
            break;
        }
        case 2: {
            var tempPt = new BMapGL.Point(121.48020807481275, 31.235898502979378);
            window.map.centerAndZoom(tempPt, 12);
            document.body.style.backgroundImage = "url('/img/shanghai.png')";
            break;
        }
        case 3: {
            var tempPt = new BMapGL.Point(113.27173638634481, 23.138748561907633);
            window.map.centerAndZoom(tempPt, 12);
            document.body.style.backgroundImage = "url('/img/guangzhou.png')";
            break;
        }
        case 4: {
            var tempPt = new BMapGL.Point(114.06554649534966, 22.571939198177372);
            window.map.centerAndZoom(tempPt, 12);
            document.body.style.backgroundImage = "url('/img/shenzhen.png')";
            break;
        }
    }
}

