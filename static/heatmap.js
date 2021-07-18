function initialize_map(type) {
    window._heatmap = new BMap.Map("container");
    window._heatmap.centerAndZoom(new BMap.Point(116.418261, 32), 6);
    window._heatmap.enableScrollWheelZoom();
    window._heatmap_type = type;

    url = '/api/heatmap_' + type.toString() + '/';
    console.log(url);

    var points;
    $.ajax({
        url: url,
        async: false,
        type: "GET",
        dataType: 'json',
        headers: { 'Access-Control-Allow-Origin': '*' },
        contentType: "application/json",
        xhrFields: { withCredentials: false },
        crossDomain: true,
        success: function (res) {
            points = res.data;
        }
    });

    window.heatmapOverlay = new BMapLib.HeatmapOverlay({ "radius": 30 });
    window._heatmap.addOverlay(window.heatmapOverlay);
    window.heatmapOverlay.setDataSet({ data: points, max: 1000 });
}

function toggle() {
    window.heatmapOverlay.toggle()
}

function refresh_heatmap(type) {
    if (type != window._heatmap_type) {
        document.getElementById('container').innerHTML = "";
        initialize_map(type)
    }
}