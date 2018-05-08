// Define the `app` module
var app = angular.module('app', []);



// Define the `PhoneListController` controller on the `app` module
app.controller('PhoneListController', ['$scope', '$http', '$timeout', function ($scope, $http, $timeout) {

    var foamtree = new CarrotSearchFoamTree({
      id: "visualization",
    });


    $('#radioBtn a').tooltip({
        placement: "bottom",
        trigger: "hover"
    });
    $('[data-toggle="tooltip"]').tooltip();

    $('#radioBtn a').on('click', function(){
        var val = $(this).text();
        var engine = val.toLowerCase();
//        console.log(val);
        var sel = $(this).data('title');
        var tog = $(this).data('toggle');
        $('#'+tog).prop('value', sel);

        $('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active').addClass('notActive');
        $('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive').addClass('active');

        drawChart(request, engine);
    });
//  Clustering.js
    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');
    //console.log(window.location.href);
    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    $('#summary a').attr('href', '/summary/?request='+ encodeURI(request));
    $('#analysis a').attr('href', '/analysis/?request=' + encodeURI(request));
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(request));
    $('#clustering a').attr('href','/clustering/?request=' + encodeURI(request));


    //var modal_closed_flag = false;
    //var last_response = null;

    //$("#helpModal").on('hide.bs.modal', function () {
     //       drawChart(request, "lingo");
    //});

    $(".glyphicon-info-sign").on('hover', function () {
            $('[data-toggle="tooltip"]').tooltip();
    });

    drawChart(request, "lingo");

    function drawChart(request, engine) {
        //console.log("Drawing Chart with algo=", engine);

        $scope.phones = [];

        function load_table(data) {
            //console.log(data);
            $scope.phones = [];
            $timeout(function() {
                $scope.phones = data;
            }, 0);
        }

        Array.prototype.removeValue = function(name, value){
           var array = $.map(this, function(v,i){
              return v[name] === value ? null : v;
           });
           this.length = 0; //clear original array
           this.push.apply(this, array); //push all elements except the one we want to delete
        }

        function convert(clusters) {

        //clusters.removeValue("other-topics", true);

//        console.log("-------------------------Clusters-----------------------------------------")
        //console.log(clusters)
        return clusters.map(function(cluster) {
            for(var propertyName in cluster) {
               // propertyName is what you want
               // you can get the value like this: myObject[propertyName]
        }
        return {
              id:     cluster.docs,
              label:  cluster.labels,
              weight: cluster.attributes && cluster.attributes["other-topics"] ? 0 : cluster.docs.length,
              groups: cluster.clusters ? convert(cluster.clusters) : []
        }
        });
        }

        // Clear the previous model.
        foamtree.set("dataObject", null);
        foamtree.set("logging", true);



        if(request.localeCompare('Kelloggs')==0){

            url = "http://localhost:8983/solr/kelloggs/clustering?clustering.engine="+ engine +"&wt=json&indent=true"
        }
        else if(request.localeCompare('Cars')==0){

            url = "http://localhost:8983/solr/cars/clustering?clustering.engine="+ engine +"&wt=json&indent=true"
        }
        else
        {
            if(request.indexOf('.csv')!=-1)
            {
                $http.get("http://localhost:8983/solr/MY_PRODUCT3/dataimport?command=full-import").then(function(response) {
                    console.log(response);
                    });
                url = "http://localhost:8983/solr/MY_PRODUCT3/clustering?q=pCategory:"+ request.substring(0,request.length-4) +"&clustering.engine="+ engine +"&wt=json&indent=true";
                console.log(request.substring(0,request.length-4));
            }
            else{
               $http.get("http://localhost:8983/solr/MY_PRODUCT/dataimport?command=full-import").then(function(response) {
                    console.log(response);
                    });
                url = "http://localhost:8983/solr/MY_PRODUCT/clustering?q=pCategory:"+ request +"&clustering.engine="+ engine +"&wt=json&indent=true";
            }
        }
        $http.get(url).then(function(response) {
            console.log("parsing response for clustering")
            console.log("Response = ", response)
            console.log('data = ', response.data)
            console.log('length of response.data.clusters > ')


                console.log(response.data.clusters.length);
                //last_response = response;
                //console.log(response.data.response.numFound)
                if (response.data.response.numFound > 1){

                foamtree.set({
                    dataObject: {
                    groups: convert(response.data.clusters)
                    },

                    onGroupSelectionChanged: function(info) {
                    //console.log("info > ");
                    console.log(info);

                    var selectedClusterObjects = [];
                    selectedCluster = {};

                    function findText(element) {
                        //console.log("data.response.docs = ", response.data.response.docs)
                        //console.log("inside findText()");
                        response.data.response.docs.forEach(function(e)  {

                            if(request.localeCompare('Kelloggs')==0){
                                if(element.localeCompare(e.t_id) == 0){
                                            //console.log("e.rtext = ", e.rText)
                                            selectedCluster.rText = e.t_text;
                                            selectedCluster.rTitle = e.t_title;
                                            selectedCluster = {};
                                            selectedClusterObjects.push(selectedCluster)
                                            //console.log(selectedClusterObjects)
                                        }
                            }
                            else if(request.localeCompare('Cars')==0){
                                if(element.localeCompare(e.c_id) == 0){
                                            //console.log("e.rtext = ", e.rText)
                                            selectedCluster.rText = e.c_text;
                                            selectedCluster.rTitle = e.c_title;
                                            selectedCluster = {};
                                            selectedClusterObjects.push(selectedCluster)
                                            console.log(selectedClusterObjects)
                                        }
                            }
                            else {
                                    if(element.localeCompare(e.rid) == 0){
                                        //console.log("e.rtext = ", e.rText)
                                        selectedCluster.rText = e.rText;
                                        selectedCluster.rTitle = e.rTitle;
                                        selectedCluster = {};
                                        selectedClusterObjects.push(selectedCluster);
                                        //console.log("selected cluster");
                                        //console.log(selectedCluster);
                                    }
                            }
                        })
                    }

                    //console.log(info.groups[0].id.length);

                    info.groups[0].id.forEach(function(ele) {
                        //console.log(ele)
                        findText(ele)
                    });
                    //console.log(reviewText)
                    //console.log(selectedClusterObjects)
                    load_table(selectedClusterObjects)
                    },
    //                groupColorDecorator: function(opts, params, vars) {
    //                    // Sentiment is a custom property with values in the -1..+1 range.
    //                    // -1 means negative sentiment, +1 -- positive, 0 -- neutral.
    //
    //                    var id_sentiment = 0;
    //                    //console.log("response.data.response.docs = ", response.data.response.docs)
    //
    //                    function findSentiment(element, group_s) {
    //                        // console.log("response.data.response.docs = ", response.data.response.docs)
    //                       response.data.response.docs.forEach(function(e)  {
    //                                   if(element.localeCompare(e.rid) == 0){
    //    //                                    console.log("e= ", e)
    //    //                                    console.log("group sentiment", group_sentiment)
    //    //                                    console.log(e.sentiment[0])
    //                                       if(e.sentiment[0].localeCompare("Positive") == 0)
    //                                           id_sentiment = 1;
    //                                       else if(e.sentiment[0].localeCompare("Negative") == 0)
    //                                           id_sentiment = -5;
    //                                       else
    //                                           id_sentiment = 0;
    //
    //                                       group_s += id_sentiment;
    //
    //       //                                console.log(selectedCluster)
    //                                   }
    //                       });
    //
    //                        // console.log(group_s, group_sentiment)
    //
    //                        return group_s;
    //                    }
    //
    //                    var group_s = 0;
    //                    params.group.id.forEach(function(ele) {
    //                        //console.log(ele);
    //                        group_s = findSentiment(ele, group_s);
    //                    });
    //                    //group_s = 0;
    //                    params.group.sentiment = group_s;
    //                    // console.log("group sentiment=", group_sentiment, group_s);
    //                    // group_sentiment = 0;
    //
    //                    var sentiment = params.group.sentiment;
    //                    if (sentiment === undefined || sentiment == 0) {
    //                      // Make neutral groups grey
    //                      vars.groupColor.s = 0;
    //                      vars.groupColor.l = 0;
    //                      vars.groupColor.a = 0.2;
    //                    } else {
    //                      if (sentiment > 0) {
    //                        // Make positive groups green
    //                        vars.groupColor.h = 120;
    //                      } else {
    //                        // Make negative groups red
    //                        vars.groupColor.h = 0;
    //                      }
    //
    //                      // Make saturation and lightness depend on
    //                      // the strength of the sentiment.
    ////                      vars.groupColor.s = 50 * (1 + Math.abs(sentiment));
    ////                      vars.groupColor.l = Math.abs(60 * sentiment);
    ////                      vars.groupColor.a = 0.5;
    //                    }
    //                    // Indicate that we use the HSLA model
    //                    vars.groupColor.model = "hsla";
    //                },

                });



        //        console.log(foamtree.get("selection").groups);
                //console.log(data.response.docs)
                load_table(response.data.response.docs);

             }
             else if (response.data.response.numFound == 0){
                $('#chartArea').children().removeClass('active');
                $('#chartArea').children().addClass('hidden');
                $('#chartArea').text('Data for the request not present!');
             }

          }//success response
          , function(response){

                console.log(response);
          });
    }

    $.get('/service/request/').then(function (successResponse) {

}, function (errorResponse) {

        console.log("errorResponse", errorResponse)
});

    //$scope.$apply();
}]);
