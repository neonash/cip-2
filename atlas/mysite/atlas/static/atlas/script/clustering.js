(function(){

    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');
    //console.log(window.location.href)
    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    $('#analysis a').attr('href', '/analysis/?request=' + encodeURI(request))
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(request))
    $('#clustering a').attr('href','/clustering/?request=' + encodeURI(request))
    $('#comparison a').attr('href','/compare/?request=' + encodeURI(request))


    var foamtree = new CarrotSearchFoamTree({
      id: "visualization",
      dataObject: {
        groups: [
          { label: "Your", weight: 1.0 },
          { label: "First", weight: 3.0 },
          { label: "FoamTree", weight: 2.0 },
          { label: "Visualization", weight: 4.0 }
        ]
      },
//      onGroupSelectionChanged: function(info) {
//          //alert(info.groups.length + " group(s) selected");
//          console.log(info.groups[0])
//      },
      //rainbowStartColor: "#f00",
      //rainbowEndColor: "#aa0",


    });



    function convert(clusters) {
    console.log("-------------------------Clusters-----------------------------------------")

    return clusters.map(function(cluster) {
        for(var propertyName in cluster) {
           // propertyName is what you want
           // you can get the value like this: myObject[propertyName]
        //console.log(propertyName)
    }
    return {
          id:     cluster.docs,
          label:  cluster.labels,
          weight: cluster.attributes && cluster.attributes["other-topics"] ? 0 : cluster.docs.length,
          groups: cluster.clusters ? convert(cluster.clusters) : []
    }
    });
    };

    // Clear the previous model.
    foamtree.set("dataObject", null);
    foamtree.set("logging", true);
    url = "http://localhost:8983/solr/MY_PRODUCT/clustering?q=pCategory:"+ request +"&clustering.engine=stc&wt=json&indent=true"

//    $.get(url).then(function (data) {
//        foamtree.set({
//          dataObject: {
//            groups: convert(data.clusters)
//          },
//        });
//    },function(errorResponse){
//        console.log('errorResponse', errorResponse);
//    });


    //First import latest data to Solr


    // Load Carrot2 JSON clusters
    $.ajax({
      //url: "http://localhost:8983/solr/MY_PRODUCT/clustering?q=*:*&rows=7569&wt=json",
      url: url,
      dataType: "json",
      success: function(data) {
      console.log(data)
        foamtree.set({
            dataObject: {
            groups: convert(data.clusters)
            },
            onGroupSelectionChanged: function(info) {
            //alert(info.groups.length + " group(s) selected");
            //console.log(info.groups[0])
            var reviewText = []
            function findText(element) {
                //console.log(data.response.docs)
                data.response.docs.forEach(function(e)  {
                            if(element.localeCompare(e.rid) == 0){
                                //console.log(e.rText)
                                reviewText.push(e.rText)
                            }
                })
                //console.log(a)
                //return a
            }
            //console.log(info.groups[0].id.length)

            info.groups[0].id.forEach(function(ele) {
                //console.log(ele)
                findText(ele)
            });
            console.log(reviewText)
            },
//          groupColorDecorator: function(opts, params, vars) {
//              // Sentiment is a custom property with values
//              // in the -1..+1 range, -1 menas negative
//              // sentiment, +1 -- positive, 0 -- neutral
//              var sentiment = params.group.sentiment;
//              //console.log(opts)
//              if (sentiment == 0) {
//                // Make neutral groups grey
//                vars.groupColor.s = 0;
//                vars.groupColor.l = 0;
//              } else {
//                if (sentiment > 0) {
//                  // Make positive groups green
//                  vars.groupColor.h = 120;
//                } else {
//                  // Make negative groups red
//                  vars.groupColor.h = 0;
//                }
//
//                // Make saturation and lightness depend on
//                // the strength of the sentiment.
//                vars.groupColor.s = 50*(1+Math.abs(sentiment));
//                vars.groupColor.l = Math.abs(60 * sentiment);
//
//                // Indicate that we use the HSL model
//                vars.groupColor.model = "hsl";
//              }
//          },
              relaxationVisible: true,
              // Make the relaxation last longer
              relaxationQualityThreshold: 0,
              relaxationMaxDuration: 15000,

              // For faster rendering
              groupFillType: "plain"
        });
//        console.log(foamtree.get("selection").groups);

      }//success response
    });


})();