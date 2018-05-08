(function(){
    console.log("Inside analysis.js");
    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');

    $('#circle-highlight-edit1').removeClass('fa-circle-o');
    $('#circle-highlight-edit1').addClass('fa-dot-circle-o');

    $('.selectpicker').selectpicker({
        size: 4
    });

    $('.selectpicker').selectpicker('selectAll');

    var query = window.urlUtils.getQueryParameter(window.location.href, 'request');
    query="headphones";
    var flag;
    console.log(query);

    $('#summary a').attr('href', '/summary/?request='+ encodeURI(query))
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(query))
    $('#analysis a').attr('href', '/analysis/?request='+ encodeURI(query))
    $('#clustering a').attr('href', '/clustering/?request='+ encodeURI(query))


    load_brand1();
    flag = 0;
    var dict_inland_products;

    function load_all_charts()
    {
        load_chart1();
        load_chart2();
        load_chart3();
        load_chart4();
        load_chart5();
    }

    function load_brand1() {
        console.log("Brand called")
        $.ajax({
            type: "GET",
            url: "/service/analysis_brand1/",
            data: { 'query': query },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {
//              console.log(response)
                var $brand = $('#brand1');
                $("#Chart1select .selectpicker").selectpicker();
                $brand.find('option').remove();

               $.each(response, function (key, value) {
                   if (value.pBrand != null) {
                       $('<option/>').val(value.pBrand).text(value.pBrand).appendTo($brand);
                   }
                });
                $('#brand1').selectpicker('refresh');
                //$("#Chart1select").selectpicker("refresh");
                $('#brand1').selectpicker('selectAll');

                load_source1();
            },
            failure: function (response) {
                alert("failed");
            }
        });
    }


    function load_source1() {
//      console.log($('#brand1').val())
        var brand = JSON.stringify($('#brand1').val());
        console.log(brand);
        $.ajax({
            type: "GET",
            url: "/service/analysis_source1/",
            data: { 'query': query , 'brand': brand },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {
//              console.log(response)
                var $source = $('#source1');
                $source.find('option').remove();

                $.each(response, function (key, value) {
//                  console.log("Key:", key);
//                  console.log("Value:", value.siteCode);
                    if (value.siteCode != null) {
                        $('<option/>').val(value.siteCode).text(value.siteCode).appendTo($source);
                    }
                });
                $("#source1").selectpicker("refresh");
                $('#source1').selectpicker('selectAll');

                load_sku1();
            },
            failure: function (response) {
             alert("failed");
            }
        });
    }


    function load_sku1() {
//        console.log($('#source1').val());
        $.ajax({
            type: "GET",
            url: "/service/analysis_sku1/",
            data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val())},
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (response) {
                //console.log(response)
                var $sku = $('#sku1');
                $sku.find('option').remove();

               $.each(response, function (key, value) {
//                console.log("Key:", key)
//                console.log("Value:", value.pModel)
                  if (value.pModel != null) {
                    $('<option/>').val(value.pModel).text(value.pModel).appendTo($sku);
                   }
                });
                $("#sku1").selectpicker("refresh");
                $('#sku1').selectpicker('selectAll');
                if(1){
                    load_all_charts();
                }
            },
            failure: function (response) {
                alert("failed");
            }
        });
    }


function load_chart1() {
        console.log("Loading chart1");
//      console.log($('#sku1').val())

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/analysis_chart1/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
       , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate))},
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response);

                Highcharts.chart('line-chart', {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: ' Overall Sentiments by Brand'
                    },
                    subtitle: {
                        text: 'Click the columns for sentiments at SKU level'
                    },
                    xAxis: {
                        type: 'category'
                    },
                    yAxis: {
                        title: {
                            text: 'Brand Positivity'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                    plotOptions: {
                        series: {
                            //borderWidth: 0,
                            dataLabels: {
                                enabled: true,
                                format: '{point.y:.1f}%'
                            }
                        }
                    },

                    tooltip: {
                        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b><br/>'
                    },

                    series: [{
                        name: 'Brands',
                        colorByPoint: true,
                        data: response[0]
                    }],
                    drilldown: {
                        series: response[1]
                    }
                });
              //console.log(response);
       },
       failure: function (response) {
           alert("failed");
       }
    });
}


function load_chart2() {
        console.log("Loading chart2");
//      console.log($('#sku1').val())

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/analysis_chart2/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
       , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate))},
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response);

            Highcharts.chart('bar-chart', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: 'Overall Sentiments by Source'
                },
                xAxis: {
                    categories: ['Positive', 'Negative', 'Neutral']
                },
                yAxis: {
                    title: {
                        text: ''
                    },
                    labels: {
                        overflow: 'justify'
                    }
                },
                credits: {
                    enabled: true
                },
                series: response
            });
           //console.log(response);
       },
       failure: function (response) {
           alert("failed");
       }
    });
}


    function load_chart3() {
        console.log("Loading chart3");
//      console.log($('#sku1').val())

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/analysis_chart3/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
       , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate))},
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response[1].toString());

               var data1 = response[0];
//              var data1 = [{
//				    name: 'Upgrade',
    //				y: 88.88,
    //				drilldown: null
//		            },
        //			{
        //				name: 'Replace',
        //				y: 10.38,
        //				drilldown: null
        //			},
        //			{
        //				name: 'First Purchase',
        //				y: 24.03,
        //				drilldown: null
        //			},
        //			{
        //				name: 'Gift',
        //				y: 4.77,
        //				drilldown: 'Gift'
        //			},
        //			{
        //				name: 'Marketing Sale',
        //				y: 0.91,
        //				drilldown: null
        //			}];

                var data2 = response[1];

//              var data2 = [{
//                        name: 'Gift',
//                        id: 'Gift',
//                        data: [
//                            ['Birthday', 13.333],
//                            ['Wedding', 0.77],
//                            ['Christmas', 0.42],
//                            ['Other', 0.3]
//                        ]
//                    }];

            Highcharts.chart('donut-chart1', {
                   credits: {
                        enabled: true
                    },
                    chart: {
                        type: 'pie'
                    },
                    title: {
                        text: 'Triggers of Purchase',
                        //style: { fontSize: '12px' },
                    },
                    plotOptions: {
                        pie:{
                            dataLabels: {
                                enabled: true
                            },
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.1f}%</b> <br/>'
                    },
                    series: [{
                        name: 'Triggers',
                        colorByPoint: true,
                        data: data1
                    }],
                    drilldown: {
                        series: data2
                    }
                });

           //console.log(response);
       },
       failure: function (response) {
           alert("failed");
       }
    });
}

function load_chart4() {
    console.log("Loading chart4");
//    console.log($('#sku1').val())

    fromDate = $("#from").datepicker( "getDate" )
    toDate = $("#to").datepicker( "getDate" )

    $.ajax({
       type: "GET",
       url: "/service/analysis_chart4/",
       data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
       'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
       , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate))},
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
           //console.log(response[1].toString());

           var data1 = response[0];
//           var data1 = [{
//				name: 'Upgrade',
//				y: 88.88,
//				drilldown: null
//		    },
//			{
//				name: 'Replace',
//				y: 10.38,
//				drilldown: null
//			},
//			{
//				name: 'First Purchase',
//				y: 24.03,
//				drilldown: null
//			},
//			{
//				name: 'Gift',
//				y: 4.77,
//				drilldown: 'Gift'
//			},
//			{
//				name: 'Marketing Sale',
//				y: 0.91,
//				drilldown: null
//			}];

            var data2 = response[1];

//            var data2 = [{
//                        name: 'Gift',
//                        id: 'Gift',
//                        data: [
//                            ['Birthday', 13.333],
//                            ['Wedding', 0.77],
//                            ['Christmas', 0.42],
//                            ['Other', 0.3]
//                        ]
//                    }];

            Highcharts.chart('donut-chart2', {
                   credits: {
                        enabled: true
                    },
                    chart: {
                        type: 'pie'
                    },
                    title: {
                        text: 'Drivers of Purchase',
                        //style: { fontSize: '12px' },
                    },
                    plotOptions: {
                        pie:{
                            dataLabels: {
                                enabled: true
                            },
                            showInLegend: true
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.1f}%</b> <br/>'
                    },
                    series: [{
                        name: 'Drivers',
                        colorByPoint: true,
                        data: data1
                    }],
                    drilldown: {
                        series: data2
                    }
                });

           //console.log(response)
       },
       failure: function (response) {
           alert("failed");
       }
    });
}
var counter=0;
function load_chart5(){
    $.ajax({
       type: "GET",
       url: "/service/summary_chart2/",
       data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
           , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {

           console.log(response['response1'])

           /*$.each(response['dict2'],function(k,v){
                                    counter += 1;
                                    console.log(v[0]);
           });
           console.log("counter is"+counter);*/

            $(response['dict2']).each(function(index){
                console.log("inside index loop");
                console.log("index is "+response['dict2'][index]);
            });

           Highcharts.chart('column-chart-rating', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Average Rating by Brand'
                },
                subtitle: {
                    text: 'Click the columns to view SKU level data. '
                },
                xAxis: {
                    type: 'category',
                    labels: {
                         enabled:false//default is true
                         }
                },
                yAxis: {
                    title: {
                        text: 'Average Rating'
                    }
                },
                legend: {
                    enabled: false
                },
                plotOptions: {
                    series: {
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true,
                            color: '#000000',
                            style: {
                                /*fontWeight: 'bolder',*/
                                /*font:'bold',*/
                                fontWeight: 'none',
                                /*fontSize:13,*/
                                textDecoration: 'none',
                             },
                            useHTML:true,
                            /*formatter: function() {
                                return '<div class="datalabel" style="position: relative; top: 0px"><b>'+ this.point.y.toFixed(2) +'</div><br/><div class="datalabelInside" style="position: relative;left: 10px;top: 60px  "><b>'+this.point.name  +'</div>';
                            },*/
                            formatter: function() {
                                console.log("drilldown data is"+response['dict2'][0]);
                                /*var counter =0;
                                $.each(response['dict2'],function(k,v){
                                    counter=counter+1;
                                    *//*dict_inland_products=v[0];
                                    console.log(typeof(dict_inland_products));
                                    console.log("inside first .each loop");
                                    console.log(v[2]);
                                    console.log(typeof(k));
                                    console.log(typeof(v));
                                    console.log("k i "+k);
                                    console.log("v is "+v);
                                    $.each(v,function(k,v){
                                        console.log("interior loop");
                                        console.log(k);
                                        console.log(v);
                                    });*//*
                                });*/
                                /*console.log("counter is"+counter);*/
                                if(this.point.y.toFixed(2) > 4.5){
                                    if(this.point.name.indexOf(' ') >= 0){
                                         return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+'<br/>'+'<br/>'+'<br/>'+"<br/><div class='datalabelInside1'>" + this.point.name.substr(0, this.point.name.indexOf(' ')+1)+'<br/>'+this.point.name.substr(this.point.name.indexOf(' ')+1 + '</div>');
                                    }else{
                                        return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+'<br/>'+'<br/>'+'<br/>'+'<br/>'+"<br/><div class='datalabelInside1'>"+this.point.name+'</div>';
                                    }
                                }else if(this.point.y.toFixed(2) > 3.5 && this.point.y.toFixed(2) < 4.5){
                                    if(this.point.name.indexOf(' ') >= 0){
                                        return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+'<br/>'+"<br/>"+ this.point.name.substr(0, this.point.name.indexOf(' ')+1)+'<br/>'+this.point.name.substr(this.point.name.indexOf(' ')+1);
                                    }else{
                                        return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+'<br/>'+'<br/>'+"<br/><div class='datalabelInside1'>"+ this.point.name + '</div>';
                                    }
                                }else if(this.point.y.toFixed(2) > 2.5 && this.point.y.toFixed(2) < 3.5){
                                    return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+"<br/><div class='datalabelInside1'>"+this.point.name + '</div>';
                                }else if(this.point.y.toFixed(2) > 1.5 && this.point.y.toFixed(2) < 2.5){
                                    return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + '<br/>'+'<br/>'+"<br/><div class='datalabelInside1'>"+ this.point.name + '</div>';
                                }else{
                                    return "<div class='datalabelInside'><span style='color: 'black';'> <b>" + this.point.y.toFixed(2) + '</b></span></div>' + "<div class='datalabelInside1'>" + this.point.name + '</div>';
                                }

                            },
                            verticalAlign: 'top', // Position them vertically in the top
                            /*formatter: function() {return this.point.y.toFixed(2) + '<br>' + '   ' + '<br>' + this.point.name},*/
                            //verticalAlign:'bottom',
                            inside: true
                        },
                        pointWidth: 100
                    }
                },

                tooltip: {
                    headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
                    pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}'
                },
                series: [{
                        name: 'Brands',
                        colorByPoint: true,
                        data : response['response1']
                }],

                /*drilldown: response['dict2'],*/
                drilldown: {

                     activeDataLabelStyle: {
                        color: 'black',
                        textDecoration: 'none',
                        fontWeight: 'none',
                        font: 'none'
                        /*fontStyle: 'bold'*/
                    },
                    series: [{
                        id: 'Brands',
                        data : response['dict2']
                    }],
                }



            });

       },
       failure: function (response) {
           alert("failed");
       }
    });

}


    $('#brand1').on('change', function(){
        var selected = [];
        brand = $('#brand1').val();
        source = $('#source1').val();
        sku = $('#sku1').val();
        //console.log(brand,source,sku); //You get the multiple values selected in your array
        console.log(JSON.stringify($('#sku1').val()));
        load_source1();
    });

    $('#source1').on('change', function(){
        var selected = [];
        brand = $('#brand1').val();
        source = $('#source1').val();
        sku = $('#sku1').val();
        //console.log(brand,source,sku); //You get the multiple values selected in your array
        console.log(JSON.stringify($('#sku1').val()));
        load_sku1();
        });

    $('#sku1').on('change', function(){
        var selected = [];
        brand = $('#brand1').val();
        source = $('#source1').val();
        sku = $('#sku1').val();
        //console.log(brand,source,sku); //You get the multiple values selected in your array
        console.log(JSON.stringify($('#sku1').val()));
        load_all_charts();
    });

    //$( "#datepicker" ).datepicker();

    var dateFormat = "mm/dd/yy",
      from = $( "#from" )
        .datepicker({
          showWeek: true,
          firstDay: 1,
          defaultDate: "+1w",
          changeMonth: true,
          numberOfMonths: 1
        })
        .on( "change", function() {
          to.datepicker( "option", "minDate", getDate( this ) );
          //console.log(date);
          load_all_charts();

        }),
      to = $( "#to" ).datepicker({
        showWeek: true,
        firstDay: 1,
        defaultDate: "+1w",
        changeMonth: true,
        numberOfMonths: 1
      })
      .on( "change", function() {
        from.datepicker( "option", "maxDate", getDate( this ) );
    //    date = $("#to").datepicker( "getDate" )
    //    day  = date.getDate(),
    //    month = date.getMonth() + 1,
    //    year =  date.getFullYear();
        //console.log(day, month, year);
        load_all_charts();

      });

    function getDate(element) {
      var date;
      try {
        date = $.datepicker.parseDate( dateFormat, element.value );
      } catch( error ) {
        date = null;
      }

      return date;
    }



    $.get('/service/request/').then(function (successResponse) {},
    function (errorResponse) {
            console.log("errorResponse", errorResponse)
    });

})();
