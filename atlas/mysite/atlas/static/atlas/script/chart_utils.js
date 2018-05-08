(function(){
    chartUtils.drawBarChart = function (options) {
        console.log('draw barchart')
        var myChart = Highcharts.chart(options.chartContainerId, {
                chart: {
                    renderTo: options.chartContainerId,
                    type    : 'bar'
                },
                title: {
                    text: options.title
                },
                xAxis: options.xAxis,
                yAxis: options.yAxis,
                series: options.series
            });
    }

})(window.chartUtils || (window.chartUtils = {}));
