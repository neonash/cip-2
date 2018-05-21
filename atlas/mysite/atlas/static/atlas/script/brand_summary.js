(function() {

$('#parent').removeClass('hidden');
$('#parent').addClass('active');

$('.selectpicker').selectpicker({
  size: 4
});

$('.selectpicker').selectpicker('selectAll');
console.log(window.location.href);
var query = window.urlUtils.getQueryParameter(window.location.href, 'request');
console.log(query);
$('#summary a').attr('href', '/summary/?request='+ encodeURI(query));
$('#analysis a').attr('href', '/analysis/?request='+ encodeURI(query));
$('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(query));
$('#clustering a').attr('href', '/clustering/?request='+ encodeURI(query));
 $('#pivot a').attr('href','/pivot/?request=' + encodeURI(query));
    $('#association a').attr('href','/association/?request=' + encodeURI(query));

//$('#comparison a').attr('href', '/compare/?request='+ encodeURI(query));


console.log("Changed analysis href");
//console.log("Inside brand summary")

var flag;  // True if query string contains '.csv', else False
console.log(query);
if(query.indexOf('.csv')!=-1){
        flag = true;
    }
    else{
        flag = false;
    }

var top_pos_neg_resp = [];

if(flag == true){
        $('#header_filters').removeClass('active');
        $('#header_filters').addClass('hidden');

        load_count_cards();
        load_all_charts();
    }
    else{  // flag == false
        $('#header_filters').removeClass('hidden');
        $('#header_filters').addClass('active');
        load_brand1();
    }


function load_count_cards()
{
    if (flag == false){

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/summary_countRevCards/",

           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
           , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
                console.log(response);
                $('#totalbox').text(response[0]);
                $('#positivebox').text(response[1]);
                $('#negativebox').text(response[2]);
           },
           failure: function (response) {
               alert("failed");
               $('#totalbox').text("0");
               $('#positivebox').text("0");
               $('#negativebox').text("0");
           }
        });
     }
     else{  // if flag is true
         $.ajax({
           type: "GET",
           url: "/service/summary_countRevCardsOverall/",

           data: { 'query': query  },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
                console.log(response);
                $('#totalbox').append(response[0]);
                $('#positivebox').text(response[1]);
                $('#negativebox').text(response[2]);
           },
           failure: function (response) {
               alert("failed");
               $('#totalbox').text("0");
               $('#positivebox').text("0");
                $('#negativebox').text("0");
           }
        });
     }
}


function load_all_charts()
    {
        load_chart1();
        //load_chart2();
        //load_chart3();
        load_pie_chart();
        load_top_pos_neg();
    }


function load_top_pos_neg(){
    if (flag == false){

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/summary_topposneg/",

           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
           , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
                //standard response includes a set of 4 records. 1st 2 being top 2 positive reviews in order,
                //and next 2 being top negative reviews in order
                parsed_resp = JSON.parse(response);
                console.log(parsed_resp);
                top_pos_neg_resp = parsed_resp;
                //to populate default positive post 1 and negative post 1
                if(parsed_resp.length == 4){ // if 4 records found, 2 are positive 2 are negative
                    $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                    $('#rPosText').text(parsed_resp[0]['fields']['rText']);
                    $('#rNegTitle').text(parsed_resp[2]['fields']['rTitle']);
                    $('#rNegText').text(parsed_resp[2]['fields']['rText']);
                }
                else if(parsed_resp.length == 3){ //1st record is anyway 1st positive post
                    $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                    $('#rPosText').text(parsed_resp[0]['fields']['rText']);
                    if(parseInt(parsed_resp[1]['fields']['rRating']) > 2){ //if second record is positive, then third record is 1st negative post
                        $('#rNegTitle').text(parsed_resp[2]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[2]['fields']['rText']);
                    }
                    else { // if second record is negative, then that is the 1st negative post
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[1]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[1]['fields']['rText']);
                    }
                }
                else if (parsed_resp.length == 2){ //if 2 records found
                    if(parseInt(parsed_resp[0]['fields']['rRating']) > 2){ //if 1st record is positive, then it is 1st positive post
                        $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rPosText').text(parsed_resp[0]['fields']['rTitle']);
                        if(parseInt(parsed_resp[1]['fields']['rRating']) > 2){ //if second record is also positive,
                        //then there are no negative records
                            $('#rNegTitle').text("No records available");
                            $('#rNegText').text("No records available");
                        }
                        else{ //if second record is negative, then that is the 1st negative post
                            $('#rNegTitle').text(parsed_resp[1]['fields']['rTitle']);
                            $('#rNegText').text(parsed_resp[1]['fields']['rText']);
                        }
                    }
                    else{ //if first record itself is negative,
                    //then that is the 1st negative post, and there are no positive records to show
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[0]['fields']['rText']);
                    }
                }
                else if(parsed_resp.length == 1){ //if 1 record found
                    if(parseInt(parsed_resp[0]['fields']['rRating']) > 2){ //if record is positive,
                    //then there are no negative records to show (even pos post 2 will be empty)
                        $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rPosText').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegTitle').text("No records available");
                        $('#rNegText').text("No records available");
                    }
                    else{ // if record is negative, then that is the 1st negative post (even neg post 2 will be empty)
                    //also there are no positive records to show
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[0]['fields']['rText']);
                    }
                }
                else{ //if no records retrieved
                    $('#rPosTitle').text("No records available");
                    $('#rPosText').text("No records available");
                    $('#rNegTitle').text("No records available");
                    $('#rNegText').text("No records available");
                }
           },
           failure: function (response) {
               alert("failed");
                $('#rPosTitle').text("Failed to retrieve data!");
                $('#rPosText').text("Please reload the page");
                $('#rNegTitle').text("Failed to retrieve data!");
                $('#rNegText').text("Please reload the page");
           }
        });
     }
     else{  // if flag is true
         $.ajax({
           type: "GET",
           url: "/service/summary_topposnegOverall/",

           data: { 'query': query  },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
                parsed_resp = JSON.parse(response);
                console.log(parsed_resp);
                top_pos_neg_resp = parsed_resp;
                //to populate default positive post 1 and negative post 1
                if(parsed_resp.length == 4){ // if 4 records found, 2 are positive 2 are negative
                    $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                    $('#rPosText').text(parsed_resp[0]['fields']['rText']);
                    $('#rNegTitle').text(parsed_resp[2]['fields']['rTitle']);
                    $('#rNegText').text(parsed_resp[2]['fields']['rText']);
                }
                else if(parsed_resp.length == 3){ //1st record is anyway 1st positive post
                    $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                    $('#rPosText').text(parsed_resp[0]['fields']['rText']);
                    if(parseInt(parsed_resp[1]['fields']['rRating']) > 2){ //if second record is positive, then third record is 1st negative post
                        $('#rNegTitle').text(parsed_resp[2]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[2]['fields']['rText']);
                    }
                    else { // if second record is negative, then that is the 1st negative post
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[1]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[1]['fields']['rText']);
                    }
                }
                else if (parsed_resp.length == 2){ //if 2 records found
                    if(parseInt(parsed_resp[0]['fields']['rRating']) > 2){ //if 1st record is positive, then it is 1st positive post
                        $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rPosText').text(parsed_resp[0]['fields']['rTitle']);
                        if(parseInt(parsed_resp[1]['fields']['rRating']) > 2){ //if second record is also positive,
                        //then there are no negative records
                            $('#rNegTitle').text("No records available");
                            $('#rNegText').text("No records available");
                        }
                        else{ //if second record is negative, then that is the 1st negative post
                            $('#rNegTitle').text(parsed_resp[1]['fields']['rTitle']);
                            $('#rNegText').text(parsed_resp[1]['fields']['rText']);
                        }
                    }
                    else{ //if first record itself is negative,
                    //then that is the 1st negative post, and there are no positive records to show
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[0]['fields']['rText']);
                    }
                }
                else if(parsed_resp.length == 1){ //if 1 record found
                    if(parseInt(parsed_resp[0]['fields']['rRating']) > 2){ //if record is positive,
                    //then there are no negative records to show (even pos post 2 will be empty)
                        $('#rPosTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rPosText').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegTitle').text("No records available");
                        $('#rNegText').text("No records available");
                    }
                    else{ // if record is negative, then that is the 1st negative post (even neg post 2 will be empty)
                    //also there are no positive records to show
                        $('#rPosTitle').text("No records available");
                        $('#rPosText').text("No records available");
                        $('#rNegTitle').text(parsed_resp[0]['fields']['rTitle']);
                        $('#rNegText').text(parsed_resp[0]['fields']['rText']);
                    }
                }
                else{ //if no records retrieved
                    $('#rPosTitle').text("No records available");
                    $('#rPosText').text("No records available");
                    $('#rNegTitle').text("No records available");
                    $('#rNegText').text("No records available");
                }
           },
           failure: function (response) {
               alert("failed");
               $('#rPosTitle').text("Failed to retrieve data!");
                $('#rPosText').text("Please reload the page");
                $('#rNegTitle').text("Failed to retrieve data!");
                $('#rNegText').text("Please reload the page");
           }
        });
     }
}


var onBrandChange = function(e) {
    console.log(e);
    load_source1();
};

var onSourceChange = function (e) {
    console.log(e);
    load_sku1();
};

var onSkuChange = function (e){
    console.log(e);
    load_count_cards();
    load_all_charts();
};



function load_brand1() {
   // console.log("Brand called")
   $.ajax({
       type: "GET",
       url: "/service/summary_brand1/",
       data: { 'query': query },
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
//           console.log(response)
            $('#brand1').off('change', onBrandChange);

           var $brand = $('#brand1');
           $("#Chart1select .selectpicker").selectpicker();
           $brand.find('option').remove();

           $.each(response, function (key, value) {
//           console.log("Key:", key)
//           console.log("Value:", value.pBrand)
               if (value.pBrand != null) {
                   $('<option/>').val(value.pBrand).text(value.pBrand).appendTo($brand);
               }
           });
          $('#brand1').selectpicker('refresh');
          //$("#Chart1select").selectpicker("refresh");
          $('#brand1').selectpicker('selectAll');

          load_source1();
          $('#brand1').on('change', onBrandChange);
       },
       failure: function (response) {
           alert("failed");
       }
   });
}


function load_source1() {
//    console.log($('#brand1').val())
    var brand = JSON.stringify($('#brand1').val())
    console.log(brand);
    $.ajax({
       type: "GET",
       url: "/service/summary_source1/",
       data: { 'query': query , 'brand': brand },
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
           $('#source1').off('change', onSourceChange);

           //console.log(response);
           var $source = $('#source1');
           $source.find('option').remove();

           $.each(response, function (key, value) {
           //console.log("Key:", key);
           //console.log("Value:", value);

               //if (value != null) {
               if (value.siteCode != null) {
                   //$('<option/>').val(value).text(value).appendTo($source);
                   $('<option/>').val(value.siteCode).text(value.siteCode).appendTo($source);
               }
           });
          $("#source1").selectpicker("refresh");
          $('#source1').selectpicker('selectAll');

          load_sku1(response);
          $('#source1').on('change', onSourceChange);

       },
       failure: function (response) {
           alert("failed");
       }
    });
}


function load_sku1(resp) { //resp is source list in full name
   //console.log(resp);

    var source_vals = null;

    /*$.ajax({
       type: "GET",
       url: "/service/summary_source1_revmap/",
       data: { 'source': resp},
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
           console.log(response);
         source_vals = response;
       },
       failure: function (response) {
           alert("failed");
       }
    });*/

    $.ajax({
       type: "GET",
       url: "/service/summary_sku1/",
       data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val())},
       //data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify(source_vals)},
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
          $('#sku1').off('change', onSkuChange);
           //console.log(response);
           var $sku = $('#sku1');
           $sku.find('option').remove();

           $.each(response, function (key, value) {
//           console.log("Key:", key)
//           console.log("Value:", value.pModel)
               if (value.pModel != null) {
                   $('<option/>').val(value.pModel).text(value.pModel).appendTo($sku);
               }
           });
           $("#sku1").selectpicker("refresh");
           $('#sku1').selectpicker('selectAll');
           if(1){
                load_count_cards();
                load_all_charts();
           }
           $('#sku1').on('change', onSkuChange);

       },
       failure: function (response) {
           alert("failed");
       }
    });
}


function load_chart1() {
    if (flag == false){

        fromDate = $("#from").datepicker( "getDate" )
        toDate = $("#to").datepicker( "getDate" )

        $.ajax({
           type: "GET",
           url: "/service/summary_chart1/",

           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
           , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response)
               $.each(response, function (key, value) {
    //           console.log("Key:", key)
    //           console.log("Value:", Date.UTC(parseInt(value[0].split('-'))))
               //value[0] = Date.UTC(parseInt(value[0].split('-')))
                //console.log(((value[0]).split('T'))[0])
                //console.log(Date.UTC(parseInt(((value[0]).split('T'))[0])))
               });
               //console.log(data1)
                   Highcharts.chart('reviewcountChart', {
                        chart: {
                            zoomType: 'x'
                        },
                        title: {
                            text: 'REVIEW FREQUENCY OVER TIME'
                        },
                        subtitle: {
                            text: document.ontouchstart === undefined ?
                                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
                        },
                        xAxis: {
                            type: 'datetime'
                        },
                        yAxis: {
                            title: {
                                text: 'Frequency'
                            }
                        },
                        legend: {
                            enabled: false
                        },

                        plotOptions: {
                            area: {
                                fillColor: {
                                    linearGradient: {
                                        x1: 0,
                                        y1: 0,
                                        x2: 0,
                                        y2: 1
                                    },
                                    stops: [
                                        [0, Highcharts.getOptions().colors[0]],
                                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                                    ]
                                },
                                marker: {
                                    radius: 2
                                },
                                lineWidth: 1,
                                states: {
                                    hover: {
                                        lineWidth: 1
                                    }
                                },
                                threshold: null
                            }
                        },

                        series: [{
                            type: 'area',
                            name: 'Count',
                            data: response
                        }]
                    });

               //console.log(response)
           },
           failure: function (response) {
               alert("failed");
           }
        });
     }
     else{  // if flag is true
         $.ajax({
           type: "GET",
           url: "/service/summary_common_reviewcount_chart/",

           data: { 'query': query },

           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               //console.log(response)
               $.each(response, function (key, value) {
    //           console.log("Key:", key)
    //           console.log("Value:", Date.UTC(parseInt(value[0].split('-'))))
               //value[0] = Date.UTC(parseInt(value[0].split('-')))
                //console.log(((value[0]).split('T'))[0])
                //console.log(Date.UTC(parseInt(((value[0]).split('T'))[0])))
               });
               //console.log(data1)
                   Highcharts.chart('reviewcountChart', {
                        chart: {
                            zoomType: 'x'
                        },
                        title: {
                            text: 'OVERALL REVIEW FREQUENCY OVER TIME'
                        },
                        subtitle: {
                            text: document.ontouchstart === undefined ?
                                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
                        },
                        xAxis: {
                            type: 'datetime'
                        },
                        yAxis: {
                            title: {
                                text: 'Frequency'
                            }
                        },
                        legend: {
                            enabled: false
                        },

                        plotOptions: {
                            area: {
                                fillColor: {
                                    linearGradient: {
                                        x1: 0,
                                        y1: 0,
                                        x2: 0,
                                        y2: 1
                                    },
                                    stops: [
                                        [0, Highcharts.getOptions().colors[0]],
                                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                                    ]
                                },
                                marker: {
                                    radius: 2
                                },
                                lineWidth: 1,
                                states: {
                                    hover: {
                                        lineWidth: 1
                                    }
                                },
                                threshold: null
                            }
                        },

                        series: [{
                            type: 'area',
                            name: 'Count',
                            data: response
                        }]
                    });

               //console.log(response)
           },
           failure: function (response) {
               alert("failed");
           }
        });
     }
}

//function load_chart2(){
//    if(flag == true){  //if '.csv' present in query string
//        $.ajax({
//           type: "GET",
//           url: "/service/summary_chart2/",
//           data: { 'query': query },
//           contentType: "application/json; charset=utf-8",
//           dataType: "json",
//           success: function (response) {
//               console.log(response['response1'])
//               Highcharts.chart('brandsummaryChart', {
//                    chart: {
//                        type: 'column'
//                    },
//                    title: {
//                        text: 'Overall Average Rating by Brand'
//                    },
//                    subtitle: {
//                        text: 'Click the columns to view SKU level data. '
//                    },
//                    xAxis: {
//                        type: 'category'
//                    },
//                    yAxis: {
//                        title: {
//                            text: 'Average Rating'
//                        }
//                    },
//                    legend: {
//                        enabled: false
//                    },
//                    plotOptions: {
//                        series: {
//                            borderWidth: 0,
//                            dataLabels: {
//                                enabled: true,
//                                format: '{point.y:.1f}'
//                            }
//                        }
//                    },
//
//                    tooltip: {
//                        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
//                        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}'
//                    },
//                    series: [{
//                            name: 'Brands',
//                            colorByPoint: true,
//                            data : response['response1']
//                    }],
//
//                    drilldown: response['dict2']
//                });
//
//           },
//           failure: function (response) {
//               alert("failed");
//           }
//        });
//    }
//    else{  //if '.csv' not present in query string
//        $.ajax({
//           type: "GET",
//           url: "/service/summary_chart2/",
//           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
//               'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
//               , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },       contentType: "application/json; charset=utf-8",
//           dataType: "json",
//           success: function (response) {
//               console.log(response['response1'])
//               Highcharts.chart('brandsummaryChart', {
//                    chart: {
//                        type: 'column'
//                    },
//                    title: {
//                        text: 'Average Rating by Brand'
//                    },
//                    subtitle: {
//                        text: 'Click the columns to view SKU level data. '
//                    },
//                    xAxis: {
//                        type: 'category'
//                    },
//                    yAxis: {
//                        title: {
//                            text: 'Average Rating'
//                        }
//                    },
//                    legend: {
//                        enabled: false
//                    },
//                    plotOptions: {
//                        series: {
//                            borderWidth: 0,
//                            dataLabels: {
//                                enabled: true,
//                                format: '{point.y:.1f}'
//                            }
//                        }
//                    },
//
//                    tooltip: {
//                        headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
//                        pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}'
//                    },
//                    series: [{
//                            name: 'Brands',
//                            colorByPoint: true,
//                            data : response['response1']
//                    }],
//
//                    drilldown: response['dict2']
//                });
//
//           },
//           failure: function (response) {
//               alert("failed");
//           }
//        });
//    }
//}

function load_chart3(){
    if(flag == false){

        $('#productcountChartDiv').removeClass('hidden');
        $('#productcountChartDiv').addClass('active');

        $.ajax({
           type: "GET",
           url: "/service/summary_chart3/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
               'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
               , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
           console.log(response);
    //        data = {
    //                'Amazon': {
    //                    'Sku1': 103,
    //                    'Sku2': 123,
    //                    'Sku3': 111,
    //                    'Sku4': 321
    //                },
    //                'HomeDepot': {
    //                    'Sku1': 500,
    //                    'Sku2': 400,
    //                    'Sku3': 302,
    //                    'Sku4': 451,
    //                    'Sku5': 651,
    //                    'Sku6': 201
    //                },
    //                'Walmart': {
    //                    'Sku1': 56,
    //                    'Sku2': 40,
    //                    'Sku3': 79,
    //                    'Sku4': 65
    //                }
    //            };
            var data = response,
                points = [],
                regionP,
                regionVal,
                regionI = 0,
                countryP,
                countryI,
                causeP,
                causeI,
                region,
                country,
                cause,
                causeName = {
                    'Communicable & other Group I': 'Communicable diseases',
                    'Noncommunicable diseases': 'Non-communicable diseases',
                    'Injuries': 'Injuries'
                };

            for (region in data) {
                if (data.hasOwnProperty(region)) {
                    regionVal = 0;
                    regionP = {
                        id: 'id_' + regionI,
                        name: region,
                        color: Highcharts.getOptions().colors[regionI]
                    };
                    countryI = 0;
                    for (country in data[region]) {
                        if (data[region].hasOwnProperty(country)) {
                            countryP = {
                                id: regionP.id + '_' + countryI,
                                name: country,
                                parent: regionP.id,
                                value : Math.round(+data[region][country])
                            };
                            regionVal += 1
                            points.push(countryP);
                            countryI = countryI + 1;
                        }
                    }
                    regionP.value = Math.round(regionVal);
                    points.push(regionP);
                    regionI = regionI + 1;
                }
            }

            //console.log(points);

            Highcharts.chart('productcountChart', {
                series: [{
                    type: 'treemap',
                    layoutAlgorithm: 'squarified',
                    allowDrillToNode: true,
                    animationLimit: 1000,
                    dataLabels: {
                        enabled: false
                    },
                    levelIsConstant: false,
                    levels: [{
                        level: 1,
                        dataLabels: {
                            enabled: true
                        },
                        borderWidth: 3
                    }],
                    data: points
                }],
                subtitle: {
                    text: 'Click points to drill down and see review count per SKU.'
                },
                title: {
                    text: 'Product distribution amongst Brands'
                }
            });

           },
           failure: function (response) {
               alert("failed");
           }
        });
    }
    else{
        $('#productcountChartDiv').removeClass('active');
        $('#productcountChartDiv').addClass('hidden');
    }
}


function load_logos(resp)
{
    console.log("inside load_logos()");
    //console.log(resp);
    var column = [];
   for(var i=0; i<resp.length; i++){
      column.push(resp[i]['name']);
   }
   $("#piechartDiv > div:first").empty();
    for (c=0; c<column.length; c++){

        var new_div = document.createElement("div");
         switch(column.length){
            case 3:
                new_div.className = "col-lg-4";
                break;
            case 2:
                new_div.className = "col-lg-6";
                break;
            case 1:
            default:
                break;
            }

        new_div.height="100%" ;

        var div_para1 = document.createElement("p");

        var para1_anchor = document.createElement("a");
        para1_anchor.target = "_blank";

        var anchor_logo = document.createElement("img");
        anchor_logo.src = "/static/atlas/images/icons/" + column[c].toString().toLowerCase() + "_logo.png";
        anchor_logo.alt = column[c];


        if(column[c].toString().toLowerCase() == "homedepot"){
            para1_anchor.href = "https://www." + column[c].toString().toLowerCase() + ".com/s/" + query;
        }
        else if(column[c].toString().toLowerCase() == "walmart") {
            para1_anchor.href = "https://www." + column[c].toString().toLowerCase() + ".com/search/?query=" + query;
        }
        else if(column[c].toString().toLowerCase() == "amazon") {
            para1_anchor.href = "https://www." + column[c].toString().toLowerCase() + ".com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + query;
        }
        para1_anchor.append(anchor_logo);

        div_para1.append(para1_anchor);

        var div_para2 = document.createElement("p");
        div_para2.innerHTML = "<b>" + column[c] + "</b>";

        new_div.append(div_para1);
        new_div.append(div_para2);

        $("#piechartDiv > div:first").append(new_div);
    }
}

function load_pie_chart(){
    if(flag == false){
        console.log("inside piechart");
        $('#piechartDiv').removeClass('hidden');
        $('#piechartDiv').addClass('active');

        $.ajax({
           type: "GET",
           url: "/service/summary_piechart/",
           data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
               'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
               , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
           console.log(response);
           load_logos(response);

            // Make monochrome colors
            var pieColors = (function () {
                var colors = [],
                    base = Highcharts.getOptions().colors[0],
                    i;

                for (i = 0; i < 10; i += 1) {
                    // Start out with a darkened base color (negative brighten), and end
                    // up with a much brighter color
                    colors.push(Highcharts.Color(base).brighten((i - 3) / 7).get());
                }
                return colors;
            }());

            Highcharts.chart('myPieChart', {
                chart: {
                    plotBackgroundColor: null,
                    plotBorderWidth: null,
                    plotShadow: false,
                    type: 'pie'
                },
                title: {
                    text: 'REVIEWS BY PLATFORM'
                },
                tooltip: {
                    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
//                legend: {
//                      enabled: true
//                  },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        colors: pieColors,
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b><br>{point.percentage:.1f} %',
                        }
                    }
                },
                series: [{
                    name: 'Platform',
                    data: response
                }]
            });

           },
           failure: function (response) {
               alert("failed");
           }
        });
    }
    else{
        $('#piechartDiv').removeClass('active');
        $('#piechartDiv').addClass('hidden');
    }
}


$("#pospost1").click(function(){  //for populating positive post 1
        if(top_pos_neg_resp){
            //if 4 records found, then first record is 1st positive,
            if((top_pos_neg_resp.length == 4) ||

                //if 3 records found, then its implied that first record is 1st positive
                ( (top_pos_neg_resp.length == 3) &&
                    (parseInt(top_pos_neg_resp[0]['fields']['rRating']) > 2) ) ||

                    //if 2 records found, only if first record's rating is high , then its 1st positive
                ( (top_pos_neg_resp.length == 2) &&
                    (parseInt(top_pos_neg_resp[0]['fields']['rRating']) > 2) ) ||

                //if only 1 record found and its rating is high, then it is 1st positive
                ( (top_pos_neg_resp.length == 1) &&
                    (parseInt(top_pos_neg_resp[0]['fields']['rRating']) > 2) )
                    ){

                $('#rPosTitle').text(top_pos_neg_resp[0]['fields']['rTitle']);
                $('#rPosText').text(top_pos_neg_resp[0]['fields']['rText']);
            }

            else{  //for any other condition
                $('#rPosTitle').text("No records available");
                $('#rPosText').text("No records available");
            }
        }
        else{  //if no records found
            $('#rPosTitle').text("No records available");
            $('#rPosText').text("No records available");
        }
    });

$("#pospost2").click(function(){//for populating positive post 2, (only if 2 positive records are there)
        if(top_pos_neg_resp){
            //if 4 records found, then second record is 2nd positive,
            if((top_pos_neg_resp.length == 4) ||

                //if 3 records found, then its implied that first record is 1st positive,
                  //but only if second record's rating is high, then second record is 2nd positive (and third record is negative)
                ( ( (top_pos_neg_resp.length == 3) || (top_pos_neg_resp.length == 2) ) &&
                    (parseInt(top_pos_neg_resp[0]['fields']['rRating']) > 2) &&
                    (parseInt(top_pos_neg_resp[1]['fields']['rRating']) > 2) )

                    //if 2 records found, only if both  record's rating is high , then second record is 2nd positive
               ){

                $('#rPosTitle').text(top_pos_neg_resp[1]['fields']['rTitle']);
                $('#rPosText').text(top_pos_neg_resp[1]['fields']['rText']);
            }

            else{  //for any other condition
                $('#rPosTitle').text("No records available");
                $('#rPosText').text("No records available");
            }
        }
        else{  //if no records found
            $('#rPosTitle').text("No records available");
            $('#rPosText').text("No records available");
        }
    });

$("#negpost1").click(function(){  // for populating negative post 1
        if(top_pos_neg_resp){
            //if 4 records found, then third record is 1st negative,
            if(top_pos_neg_resp.length == 4){
                $('#rNegTitle').text(top_pos_neg_resp[2]['fields']['rTitle']);
                $('#rNegText').text(top_pos_neg_resp[2]['fields']['rText']);
            }

            //if 3 or 2 records found, then its implied that first record is 1st positive anyway,
              //but only if second record's rating is low, then second record is 1st positive
           else if ( ( (top_pos_neg_resp.length == 3) || (top_pos_neg_resp.length == 2) ) &&
                (parseInt(top_pos_neg_resp[1]['fields']['rRating']) <= 2) ){
                    $('#rNegTitle').text(top_pos_neg_resp[1]['fields']['rTitle']);
                    $('#rNegText').text(top_pos_neg_resp[1]['fields']['rText']);
                }

            //if 2 or 1 record(s) found, only if either  record's rating is low , then that record is 1st negative
            else if ( ( (top_pos_neg_resp.length == 2) || (top_pos_neg_resp.length == 1) ) &&
                        (parseInt(top_pos_neg_resp[0]['fields']['rRating']) <= 2) )  {

                    $('#rNegTitle').text(top_pos_neg_resp[0]['fields']['rTitle']);
                    $('#rNegText').text(top_pos_neg_resp[0]['fields']['rText']);
                }
            else{  //for any other condition
                $('#rNegTitle').text("No records available");
                $('#rNegText').text("No records available");
            }
        }
        else{  //if no records found
            $('#rNegTitle').text("No records available");
            $('#rNegText').text("No records available");
        }
    });

$("#negpost2").click(function(){
        if(top_pos_neg_resp){
            // if 4 records found, then 4th record is 2nd negative
            if(top_pos_neg_resp.length == 4){
                $('#rNegTitle').text(top_pos_neg_resp[3]['fields']['rTitle']);
                $('#rNegText').text(top_pos_neg_resp[3]['fields']['rText']);
            }
            //if 3 records found, 1st record is anyway 1st positive
            //but only if second record is 1st negative, the third record will be 2nd negative
            else if( (top_pos_neg_resp.length == 3) &&
                        ( (parseInt(top_pos_neg_resp[1]['fields']['rRating']) <= 2) &&
                        (parseInt(top_pos_neg_resp[2]['fields']['rRating']) <= 2) ) ){
                $('#rNegTitle').text(top_pos_neg_resp[2]['fields']['rTitle']);
                $('#rNegText').text(top_pos_neg_resp[2]['fields']['rText']);
            }
            //if 2 records found, only if both records are negative, second record will be the 2nd negative
            else if( (top_pos_neg_resp.length == 2) &&
                        ( (parseInt(top_pos_neg_resp[0]['fields']['rRating']) <= 2) &&
                        (parseInt(top_pos_neg_resp[1]['fields']['rRating']) <= 2) ) ){
                $('#rNegTitle').text(top_pos_neg_resp[1]['fields']['rTitle']);
                $('#rNegText').text(top_pos_neg_resp[1]['fields']['rText']);
            }
            else {//for any other condition
                $('#rNegTitle').text("No records available");
                $('#rNegText').text("No records available");
            }
        }
        else{ //if no records found
            $('#rNegTitle').text("No records available");
            $('#rNegText').text("No records available");
        }

    });

//
// $('#source1').on('change', function(e){
//     console.log(e);
//     //console.log(brand,source,sku); //You get the multiple values selected in your array
//     load_sku1();
//
// });
// $('#sku1').on('change', function(e){
//     console.log(e);
//     var selected = [];
//     brand = $('#brand1').val();
//     source = $('#source1').val();
//     sku = $('#sku1').val();
//     load_chart1();
//     load_chart2();
//     load_chart3();
//
// });

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


$.get('/service/request/').then(function (successResponse) {

}, function (errorResponse) {

        console.log("errorResponse", errorResponse)
});


})();