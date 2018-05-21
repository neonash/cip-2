(function(){

    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');
    //console.log(window.location.href)
    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    $('#analysis a').attr('href', '/analysis/?request=' + encodeURI(request));
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(request));
    $('#clustering a').attr('href','/clustering/?request=' + encodeURI(request));
    $('#pivot a').attr('href','/pivot/?request=' + encodeURI(request));
    $('#association a').attr('href','/association/?request=' + encodeURI(request));

    $('#comparison a').attr('href','/compare/?request=' + encodeURI(request));

    google.load("visualization", "1", {packages:["corechart", "charteditor"]});
    $(function(){
        var derivers = $.pivotUtilities.derivers;
        var renderers = $.extend($.pivotUtilities.renderers,
            $.pivotUtilities.gchart_renderers);

//        Papa.parse("/services/mps.csv", {
//            download: true,
//            skipEmptyLines: true,
//            complete: function(parsed){
//                $("#output").pivotUI(parsed.data, {
//                    renderers: renderers,
//                    derivedAttributes: {
//                        "Age Bin": derivers.bin("Age", 10),
//                        "Gender Imbalance": function(mp) {
//                            return mp["Gender"] == "Male" ? 1 : -1;
//                        }
//                    },
//                    cols: ["Age Bin"], rows: ["Gender"],
//                    rendererName: "Area Chart"
//                });
//            }
//        });
        $.ajax({
           type: "GET",
           url: "/service/pivotparser/",
           data: { 'query': request },
           contentType: "application/json; charset=utf-8",
           dataType: "json",
           success: function (mps) {
                console.log(mps);
                $("#output").pivotUI(mps, {
                    renderers: renderers,
//                    derivedAttributes: {
//  //                            return mp["Gender"] == "Male" ? 1 : -1;                      "Age Bin": derivers.bin("Age", 10),
//                        "Gender Imbalance": function(mp) {

//                        }
//                    },
//                    cols: ["Age Bin"], rows: ["Gender"],
//                    rendererName: "Area Chart",
                    rendererOptions: {
                        gchart:{
                            height:400,
                            width:600,
                        }
                    }

                });
           },
           failure: function (response) {
               alert("failed");
           }
        });
//        $.getJSON("C:\\Users\\akshat.gupta/mps.json", function(mps) {
//            $("#output").pivotUI(mps, {
//                renderers: renderers,
//                derivedAttributes: {
//                    "Age Bin": derivers.bin("Age", 10),
//                    "Gender Imbalance": function(mp) {
//                        return mp["Gender"] == "Male" ? 1 : -1;
//                    }
//                },
//                cols: ["Age Bin"], rows: ["Gender"],
//                rendererName: "Area Chart",
//                rendererOptions: {
//                    gchart:{
//                        height:400,
//                        width:600,
//                    }
//                }
//
//            });
//        });
     });

})();