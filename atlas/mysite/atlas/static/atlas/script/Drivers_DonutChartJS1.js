var data1 = [
			{
				name: 'Brand',
				y: 64.44
			}, 
			{
				name: 'Cost',
				y: 5.08
			}, 
			{
				name: 'Recommendation',
				y: 6.71
			}, 
			{
				name: 'Innovation',
				y: 5.78
			}, 
			{
				name: 'Marketing Ads',
				y: 17.99
			}
];

//['Brand',64.44], ['Cost',17.99], ['Recommendation',5.08], ['Innovation',6.71], ['Marketing Ads',5.78]];

// Create the chart
Highcharts.chart('donut-chart2', {
	credits: {
        enabled: false
    },
    chart: {
        type: 'pie'
    },
    title: {
        text: 'Drivers of Purchase'
    },
    plotOptions: {
        series: {
            dataLabels: {
                enabled: true,
                //format: '{point.name}: {point.y:.1f}%'
            }
        }
    },
    tooltip: {
		headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
    },
    series: [{
        name: 'Drivers',
		colorByPoint: true,
        data: data1,
		innerSize: '50%'
    }]
});
