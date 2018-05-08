(function() {

$('#parent').removeClass('hidden');
$('#parent').addClass('active');

$('.selectpicker').selectpicker({
  size: 4
});

$('.selectpicker').selectpicker('selectAll');

/*var query = window.urlUtils.getQueryParameter(window.location.href, 'request');*/
var query="headphones";

$('#summary a').attr('href', '/summary/?request='+ encodeURI(query))
$('#analysis a').attr('href', '/analysis/?request='+ encodeURI(query))
$('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(query))
$('#clustering a').attr('href', '/clustering/?request='+ encodeURI(query))


console.log("Changed analysis href")
//console.log("Inside brand summary")
console.log("new changes v2")

var flag
//console.log(query)

load_brand1();
flag = 0;

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
   /* load_chart1();
    load_chart2();
    load_chart3();*/
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

//           console.log(response)
           var $source = $('#source1');
           $source.find('option').remove();

           $.each(response, function (key, value) {
//           console.log("Key:", key)
//           console.log("Value:", value.siteCode)
               if (value.siteCode != null) {
                   $('<option/>').val(value.siteCode).text(value.siteCode).appendTo($source);
               }
           });
          $("#source1").selectpicker("refresh");
          $('#source1').selectpicker('selectAll');

          load_sku1();
          $('#source1').on('change', onSourceChange);

       },
       failure: function (response) {
           alert("failed");
       }
    });
}


function load_sku1() {
//    console.log($('#source1').val())
    $.ajax({
       type: "GET",
       url: "/service/summary_sku1/",
       data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val())},
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
          $('#sku1').off('change', onSkuChange);
           //console.log(response)
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
                load_chart1();
                /*load_chart2();
                load_chart3();*/
                console.log("if (1) loop")

           }
           $('#sku1').on('change', onSkuChange);

       },
       failure: function (response) {
           alert("failed");
       }
    });
}


function load_chart1() {
//    console.log($('#sku1').val())
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
                        text: 'Review Frequency over time'
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
/*
function load_chart2(){
    $.ajax({
       type: "GET",
       url: "/service/summary_chart2/",
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

function load_chart3(){
    $.ajax({
       type: "GET",
       url: "/service/summary_chart3/",
       data: { 'query': query , 'brand': JSON.stringify($('#brand1').val()), 'source': JSON.stringify($('#source1').val()),
           'sku': JSON.stringify($('#sku1').val()), 'fromDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', fromDate))
           , 'toDate': JSON.stringify($.datepicker.formatDate('yy-mm-dd', toDate)) },
       contentType: "application/json; charset=utf-8",
       dataType: "json",
       success: function (response) {
       console.log(response)
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

}*/


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
      load_chart1();
      /*load_chart2();
      load_chart3();*/
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
    date = $("#to").datepicker( "getDate" )
    day  = date.getDate(),
    month = date.getMonth() + 1,
    year =  date.getFullYear();
    console.log(day, month, year);
   load_chart1();
    /* load_chart2();
    load_chart3();*/

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