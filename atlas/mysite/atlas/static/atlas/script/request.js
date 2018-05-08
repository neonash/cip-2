(function(){
    console.log("LOADING REQUEST JS")
    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    console.log("Request = " , request)
    $('#reqKW').val(request);

    $('#reqBtn').on('click', function (e) {
        console.log("Button clicked")
        var refresh = window.urlUtils.getQueryParameter(window.location.href, 'refresh');
        console.log(refresh)

        var type = null;
        var url= null;
        if(refresh==="true") {
            console.log("PUT CALL");
            type='PUT';
            url = "/service/product/" + encodeURI(request) + '/refresh'
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
            data:  {'name': request },
            success: function(response) {
                location.reload(false);
            },
            failure: function(response) {
                alert("Failure")
            }
        });
        console.log("ajax call request = ", request)
    });

})();