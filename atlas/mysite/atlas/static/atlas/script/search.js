(function() {
    $("#main-panel").addClass('hidden');
    $('#refresh-data').addClass('hidden');
    $('#search').addClass('active');


    var searchQuery = null;

    //Read the requests from the request queue
    $.get('/service/request/').then(function (successResponse) {
        //console.log('Stringify successResponse', JSON.stringify(successResponse,null, 2));
        //console.log('Parsed successResponse', JSON.parse(successResponse));
        var clients = [
            { "Request ID": "001", "Product": "TV", "Time": "16:54 Feb 20th 2016" , "Status": "Completed"},
            { "Request ID": "002", "Product": "iMac", "Time": "20:01 April 10th 2016" ,"Status": "Completed"},
            { "Request ID": "003", "Product": "iPad", "Time": "15:41 January 31st 2017" ,"Status": "Processing"},
            { "Request ID": "004", "Product": "iPhone", "Time": "13:09 February 15th " ,"Status": "Pending"},
            { "Request ID": "005", "Product": "Chrome Book" , "Time": "00:45 February 21st" ,"Status": "Pending"}
        ];

        $("#jsGrid").jsGrid({
            width: "100%",
            height: "400px",

            inserting: false,
            editing: false,
            sorting: true,
            paging: true,
            autoload: true,
            pageLoading: true,


            data: JSON.parse(successResponse),

            fields: [
                { name: "reqId", type: "text", width: 100, title:"Request ID" },
                { name: "reqKw", type: "text", width: 150, title: "Product" },
                { name: "reqTime", type: "text", width: 150, title: "Time" },
                { name: "reqStatus", type: "text", width: 150, title: "Status" },

            ],
            rowClick: function(args) {
                // save selected item
                selectedItem = args.item;

                // save selected row
                $selectedRow = $(args.event.target).closest("tr");

                // add class to highlight row
                $selectedRow.addClass("selected-row");
                console.log(selectedItem)
                console.log(selectedItem.reqKw)
                window.location = "../summary/?request=" + encodeURI(selectedItem.reqKw);
            },
        });
    }, function (errorResponse) {
            console.log("errorResponse", errorResponse)
    });
    /*
    $('#allCheckboxes').on("change", ":checkbox", function () {
        if (this.checked) {
            console.log(this.id + ' is checked');
            console.log(this.name + ' is checked');

        } else {
            console.log(this.id + ' is unchecked');
            console.log(this.name + ' is unchecked');

        }
    });
*/
    $('#search-query-submit').on('click', function (e) {

        var data1 = { 'site' : []};
        var site_data = []
        $(":checked").each(function() {
            data1['site'].push($(this).val());
            site_data.push($(this).val());

        });
        //console.log(data1['site'])
        console.log(site_data)

        //console.log(typeof(site_data))

        var refresh = "true";
        query = $('#search-query').val();
        console.log('searchQuery', query);

        $('.dashboard').addClass('disabled');
        $('#create-request').addClass('hidden');
        $('#request-notification').addClass('hidden');

        //$('#create-request #make-request').attr('href', '/requests/?request=');

        $.get('/service/product?query=' + query).then(function (successResponse) {
            console.log('successResponse', successResponse);
            $('#refresh-info').removeClass('hidden');
            $('#refresh-data').removeClass('hidden');
            //$('#refresh-data').attr('href', '/requests/?request='+ encodeURI(query) + '&refresh=true')
            $('#refresh-data').on('click', function(e) {

                console.log("Inside refresh");

            });
            //activateDashboard(JSON.parse(successResponse).analyticData, query)
        }, function (errorResponse) {
            console.log('errorResponse', errorResponse);
            if (errorResponse.status == "404") {
                console.log("Changing search value button to submit");
                $('#create-request').removeClass('hidden');
                //$('#create-request #make-request').attr('href', '/requests/?request='+ encodeURI(query) + '&refresh=false')
                refresh = "false"

                $('#create-request #make-request').on('click', function (e) {
                    console.log("Button clicked");
                    //var refresh = window.urlUtils.getQueryParameter(window.location.href, 'refresh');
                    console.log(refresh);
                    var type = null;
                    var url= null;
                    if(refresh==="true") {
                        console.log("PUT CALL");
                        type='PUT';
                        url = "/service/product/" + encodeURI(query) + '/refresh'
                    } else {
                        console.log("POST CALL");
                        type= 'POST';
                        url = "/service/product/add"
                    }
                    $.ajax({
                        type: type,
                        url: url,
                        headers: {
                            'X-CSRFToken': $.cookie('X-CSRFToken')
                        },
                        data:  {'name': query , 'site': JSON.stringify(site_data)},
                        success: function(response) {
                            alert("Request raised succesfully");
                            location.reload(true);

                        },
                        failure: function(response) {
                            alert("Failure")
                        }
                    });
                    console.log("Ajax call request = ", query)
                });
            }
            else
                console.log("error response : non-404");
        });
    });


    var activateDashboard = function(dashboards, request) {
        $('#main-panel').removeClass('hidden');
        console.log(dashboards["sentimentData"].length)
        console.log(dashboards["sentimentData"])
        if (dashboards["sentimentData"] && dashboards["sentimentData"].length > 0) {
            console.log("sentiment data available");
            $('#sentiment').removeClass('disabled');
            $('#sentiment').attr('href', '/sentiment/?request=' + request)
        } else {
            console.log('Nothing available')
        }
    }
})();