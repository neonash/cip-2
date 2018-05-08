(function(){
    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');

    $('.selectpicker').selectpicker({
        size: 4
    });

    $('.selectpicker').selectpicker('selectAll');

    var query = window.urlUtils.getQueryParameter(window.location.href, 'request');
    var flag;  // True if query string contains '.csv', else False
    console.log(query);
    if(query.indexOf('.csv')!=-1){
        flag = true;
    }
    else{
        flag = false;
    }


    $('#summary a').attr('href', '/summary/?request='+ encodeURI(query));
    $('#analysis a').attr('href', '/analysis/?request='+ encodeURI(query));
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(query));
    $('#clustering a').attr('href', '/clustering/?request='+ encodeURI(query));
    //$('#comparison a').attr('href', '/compare/?request='+ encodeURI(query));

    if(flag == true){
        $('#header_filters').removeClass('active');
        $('#header_filters').addClass('hidden');
        load_all_charts();
    }
    else{
        $('#header_filters').removeClass('hidden');
        $('#header_filters').addClass('active');
        load_brand1();
    }


    function load_all_charts()
    {
        if(flag==true){
            $('#brandsummaryChartDiv').removeClass('active');
            $('#brandsummaryChartDiv').addClass('hidden');
        }
        else{
            $('#brandsummaryChartDiv').removeClass('hidden');
            $('#brandsummaryChartDiv').addClass('active');
            load_brandsummary_chart();
        }
        load_senti_charts();
        load_trigdriv_charts();
    }

    function load_brandsummary_chart(){
        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )
        $.ajax({
           type: "GET",
           url: "/service/analysis_brandsummary_chart/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
               'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
               , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },       contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               console.log(response['response1'])
               Highcharts.chart('brandsummaryChart', {
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
                        type: 'category'
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
                                format: '{point.y:.1f}'
                            }
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

                    drilldown: response['dict2']
                });

           },
           failure: function (response) {
               alert("failed");
           }
        });
}


    function load_senti_charts()
    {
        if(flag == true) { //if query contains '.csv'
            $('#linechartDiv').removeClass('active');
            $('#linechartDiv').addClass('hidden');
            $('#barchartDiv').removeClass('col-lg-6');
            $('#barchartDiv').addClass('col-lg-12');
            load_common_senti_chart();
        }
        else
        {
            load_chart1();
            load_chart2();
        }
    }


    function load_common_senti_chart(){
        console.log("Loading common sentiment chart");

        $.ajax({
           type: "GET",
           url: "/service/analysis_common_senti_chart/",
           data: { 'query': query },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               console.log(response);

            Highcharts.chart('bar-chart', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: 'Overall Sentiments'
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
                 plotOptions: {
                    series: {
                        colorByPoint: true
                    }
                },
                credits: {
                    enabled: true
                },
                legend: {
                    enabled: false
                },
                series: response
            });

       },
       failure: function (response) {
           alert("failed");
       }
    });
    }

    function load_trigdriv_charts()
    {
            load_chart3();
            load_chart4();
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
                            text: 'Brand Positivity (%)'
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
                                format: '{point.y:.1f}'
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
                legend: {
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

        if(flag == false){  // if '.csv' NOT present in query string

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
                                    enabled: true,
                                    format: '<b>{point.name}</b><br>{point.percentage:.1f} %'
                                },
                                showInLegend: false
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
    else{ //if '.csv' present in query

         $.ajax({
               type: "GET",
               url: "/service/analysis_common_trig_chart/",
               data: { 'query': query },
               contentType: "application/json; charset=utf-8",
               dataType: "json",
               success: function (response) {
                   console.log(response[1].toString());

                   var data1 = response[0];
                   var data2 = response[1];

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
                                    enabled: true,
                                    format: '<b>{point.name}</b><br>{point.percentage:.1f} %'
                                },
                                showInLegend: false
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


           },
           failure: function (response) {
               alert("failed");
           }
        });
    }
}

function load_chart4() {
    console.log("Loading chart4");

    if(flag == false){  //if '.csv' NOT present in query string

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
                                    enabled: true,
                                    format: '<b>{point.name}</b><br>{point.percentage:.1f} %'
                                },
                                showInLegend: false
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
    else{  // if '.csv' present in query string
        $.ajax({
           type: "GET",
           url: "/service/analysis_common_driv_chart/",
           data: { 'query': query },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response[1].toString());

               var data1 = response[0];
               var data2 = response[1];

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
                                    enabled: true,
                                    format: '<b>{point.name}</b><br>{point.percentage:.1f} %'
                                },
                                showInLegend: false
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
