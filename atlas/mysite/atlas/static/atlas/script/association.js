(function(){

    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');
    //console.log(window.location.href)
    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    $('#summary a').attr('href', '/summary/?request='+ encodeURI(request));

    $('#analysis a').attr('href', '/analysis/?request=' + encodeURI(request));
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(request));
    $('#clustering a').attr('href','/clustering/?request=' + encodeURI(request));
    $('#pivot a').attr('href','/pivot/?request=' + encodeURI(request));
    $('#association a').attr('href','/association/?request=' + encodeURI(request));

    $('#comparison a').attr('href','/compare/?request=' + encodeURI(request));



    var onDimChange = function(e) {
        console.log(e);
    };

    var onLevChange = function (e){
    console.log(e);
    sel_dim = $('#dims').val();
    sel_lev = $('#levs').val();
    load_assoc_map(sel_dim, sel_lev);
};

//    $('#dims').on('change', function (e) {
//
//    var optionSelected = $("option:selected", this);
//    var valueSelected = this.value;
//
//    console.log(valueSelected);
//    load_assoc_map(valueSelected);
//});
//
//        $('#levs').on('change', function (e) {
//
//    var optionSelected = $("option:selected", this);
//    var valueSelected = this.value;
//
//    console.log(valueSelected);
//    load_assoc_map(valueSelected);
//});

       // console.log("dimension called");
       $.ajax({
           type: "GET",
           url: "/service/assoc_dims/",
           data: { 'query': request },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (response) {
               console.log(response);
                $('#dims').off('change', onDimChange);

               var $dim = $('#dims');
               $("#dims").selectpicker();
               $dim.find('option').remove();

               $.each(response, function (key, value) {
    //           console.log("Key:", key)
    //           console.log("Value:", value.pBrand)
                   if (value != null) {
                       $('<option/>').val(value).text(value).appendTo($dim);
                   }
               });
              $('#dims').selectpicker('refresh');
              //$("#Chart1select").selectpicker("refresh");


                var sel_dim = $("#dims option:first").val();
                        $("#dims").val(sel_dim);

                 load_levs(sel_dim);

           },
           failure: function (response) {
               alert("failed");
           }
       });



             function load_levs(sel_dim){
                // console.log("level called");
               $.ajax({
                   type: "GET",
                   url: "/service/assoc_levels/",
                   data: { 'query': request, 'dim': sel_dim },
                   contentType: "application/json; charset=utf-8",
                   dataType: "json",
                   success: function (response) {
                       console.log(response);
                        $('#levs').off('change', onLevChange);

                       var $lev = $('#levs');
                       $("#levs").selectpicker();
                       $lev.find('option').remove();

                       $.each(response, function (key, value) {
            //           console.log("Key:", key)
            //           console.log("Value:", value.pBrand)
                           if (value != null) {
                               $('<option/>').val(value).text(value).appendTo($dim);
                           }
                       });
                      $('#levs').selectpicker('refresh');
                      //$("#Chart1select").selectpicker("refresh");

                        var sel_lev = $("#dims option:first").val();
                        $("#levs").val(sel_lev);

                        load_assoc_map(sel_dim, sel_lev);

                   },
                   failure: function (response) {
                       alert("failed");
                   }
               });

            }


        function load_assoc_map(dim, lev){
        console.log("loading assoc map");
        $.ajax({
                   type: "GET",
                   url: "/service/association/",
                   data: { 'query': request, 'dim': dim, 'lev' },
                   contentType: "application/json; charset=utf-8",
                   dataType: "json",
                   success: function (response) {
                        //console.log("response = ", typeof(response))
                        d3.select("#output").selectAll("*").remove();
                        mpld3.draw_figure("output", response['graph_data']);
                        var sourceObj = eval('(' + response.source_data + ')');
            //            console.log((sourceObj));

                        for (i in sourceObj) {
                            if (sourceObj.hasOwnProperty(i)) {
                                var feature_labels = Object.keys(sourceObj[i]);
                                break;
                            }
                        }
                        //console.log(brand_labels);

                        // Radar chart code starts here



                        var marksCanvas = document.getElementById("marksChart");

                        Chart.defaults.global.defaultFontFamily = "Lato";
                        Chart.defaults.global.defaultFontSize = 18;
            //            console.log(sourceObj)

                        var sourceData = {
                          labels: feature_labels,
                          datasets: [],
            //              datasets: [{
            //                label: "Student A",
            //                backgroundColor: "transparent",
            //                borderColor: window.chartColors.red,
            //                fill: false,
            //                radius: 6,
            //                pointRadius: 6,
            //                pointBorderWidth: 3,
            //                pointBackgroundColor: "orange",
            //                pointBorderColor: "rgba(200,0,0,1)",
            //                pointHoverRadius: 10,
            //                data: [65, 75, 70, 80, 60, 80]
            //              }, {
            //                label: "Student B",
            //                backgroundColor: "transparent",
            //                borderColor: "rgba(0,0,200,1)",
            //                fill: false,
            //                radius: 6,
            //                pointRadius: 6,
            //                pointBorderWidth: 3,
            //                pointBackgroundColor: "cornflowerblue",
            //                pointBorderColor: "rgba(0,0,200,1)",
            //                pointHoverRadius: 10,
            //                data: [54, 65, 60, 70, 70, 75]
            //              }]
                        };

                        window.chartColors = {
                          red: 'rgba(255, 0, 0, 1)',
                          orange: 'rgba(255, 159, 64, 1)',
                          yellow: 'rgba(255, 205, 86, 1)',
                          green: 'rgba(75, 192, 192, 1)',
                          blue: 'rgba(0, 0, 200, 1)',
                          purple: 'rgba(153, 102, 255, 1)',
                          grey: 'rgba(231, 233, 237, 1)',
                          cornflowerblue: 'rgba(100, 149, 237, 1)',
                          deepblue: 'rgb(38, 51, 63, 1)',
                          cyan: 'rgb(70, 240, 240, 1)',
                          magenta: 'rgb(240, 50, 230, 1)',
                          lime: 'rgb(210, 245, 60, 1)',
                          pink: 'rgb(250, 190, 190, 1)',
                          teal: 'rgb(0, 128, 128, 1)',
                          lavender: 'rgb(230, 190, 255, 1)',
                          brown: 'rgb(170, 110, 40, 1)',
                          beige: 'rgb(255, 250, 200, 1)',
                          maroon: 'rgb(128, 0, 0, 1)',
                          mint: 'rgb(170, 255, 195, 1)',
                          olive: 'rgb(128, 128, 0, 1)',
                          coral: 'rgb(255, 215, 180, 1)',
                          navy: 'rgb(0, 0, 128, 1)',
                          white: 'rgb(255, 255, 255, 1)',
                          black: 'rgb(0, 0, 0, 1)',
                          darkgrey: 'rgb(192, 192, 192, 1)'
                        };

                        var combinations = [
                            {0: window.chartColors.red, 1:window.chartColors.orange},
                            {0: window.chartColors.purple, 1:window.chartColors.pink},
                            {0: window.chartColors.green, 1:window.chartColors.yellow},
                            {0: window.chartColors.orange, 1:window.chartColors.yellow},
                            {0: window.chartColors.teal, 1:window.chartColors.cyan},
                            {0: window.chartColors.navy, 1:window.chartColors.cornflowerblue},
                            {0: window.chartColors.maroon, 1:window.chartColors.brown},
                            {0: window.chartColors.olive, 1:window.chartColors.lime},
                            {0: window.chartColors.brown, 1:window.chartColors.beige},
                            {0: window.chartColors.darkgrey, 1:window.chartColors.black},
                            {0: window.chartColors.mint, 1:window.chartColors.grey},
                            {0: window.chartColors.black, 1:window.chartColors.grey},
                        ]
                        var max = 0;
                        for(i in sourceObj){
                            var newObj = {};
                            newObj.label = i;
                            var data = new Array;
                            //console.log(sourceObj[i])
                            //break;
                            for(var o in sourceObj[i]) {
                                data.push(sourceObj[i][o]);
            //                    console.log(sourceObj[i][o]);
                                if(max<sourceObj[i][o])
                                    max = sourceObj[i][o]
                            }
                            newObj.data = data
                            newObj.label = i
                            newObj.backgroundColor = "transparent"
                            newObj.fill = false
                            newObj.radius = 6
                            newObj.pointRadius = 6
                            newObj.pointBorderWidth = 3
                            newObj.pointHoverRadius = 10

                            var randomNumber = Math.floor(Math.random() * combinations.length);

                            newObj.borderColor = combinations[randomNumber][0]
                            newObj.pointBackgroundColor = combinations[randomNumber][1]
                            newObj.pointBorderColor = combinations[randomNumber][0]

                            combinations.splice(randomNumber,1)
            //                console.log(newObj)
            //                console.log(data)
                            //newObj.data = sourceObj[i];
                            //console.log(newObj)
                            sourceData.datasets.push(newObj)
            //                break;
                        }

                        console.log();

                        var chartOptions = {

            //              responsive: false,
            //              maintainAspectRatio: true,
            //              scaleOverride: true,
                          scale: {
                            gridLines: {
                              color: "black",
                              lineWidth: 3
                            },
                            angleLines: {
                              display: false
                            },
                            ticks: {
                            //Boolean - Show a backdrop to the scale label
                                showLabelBackdrop: true,

                                //String - The colour of the label backdrop
                                backdropColor: "rgba(255,255,255,0.75)",

                                //Number - The backdrop padding above & below the label in pixels
                                backdropPaddingY: 2,

                                //Number - The backdrop padding to the side of the label in pixels
                                backdropPaddingX: 2,

                                //Number - Limit the maximum number of ticks and gridlines
                                maxTicksLimit: 11,
                              beginAtZero: true,
                              min: 0,
                              max: Math.round(max / 50)*50,
                              stepSize: Math.round(max/(Object.keys(sourceObj).length/2) / 100)*100
                            },
                            pointLabels: {
                              fontSize: 18,
                              fontColor: "green",
                            }
                          },
                          legend: {
                            position: 'left'
                          }
                        };

                        var radarChart = new Chart(marksCanvas, {
                          type: 'radar',
                          data: sourceData,
                          options: chartOptions
                        });
                   },
                   failure: function (response) {
                       alert("failed");
                   }
                });
            }
    //});

})();