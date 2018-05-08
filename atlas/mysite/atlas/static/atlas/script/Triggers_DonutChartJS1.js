var data1 = [{
				name: 'Upgrade',
				y: 56.33
			}, 
			{
				name: 'Replace',
				y: 10.38
			}, 
			{
				name: 'First Purchase',
				y: 24.03
			}, 
			{
				name: 'Gift',
				y: 4.77
			}, 
			{
				name: 'Marketing Sale',
				y: 0.91
			}];
			
			//['Upgrade',56.33],['Replace',10.38], ['First Purchase',24.03], ['Gift',4.77], ['Marketing Sale',0.91],[]];

// Create the chart
Highcharts.chart('donut-chart1', {

	credits: {
        enabled: false
    },
    chart: {
        type: 'pie'
    },
    title: {
        text: 'Triggers of Purchase',
        style: { fontSize: '12px' },
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
        name: 'Triggers',
		colorByPoint: true,
        data: data1,
		innerSize: '50%'
    }]
});
