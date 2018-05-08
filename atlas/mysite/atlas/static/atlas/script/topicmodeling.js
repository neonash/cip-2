(function(){

    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');

    var request = window.urlUtils.getQueryParameter(window.location.href, 'request');
    console.log(request);

    $('#summary a').attr('href', '/summary/?request='+ encodeURI(request));
    $('#analysis a').attr('href', '/analysis/?request=' + encodeURI(request));
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(request));
    $('#clustering a').attr('href', '/clustering/?request='+ encodeURI(request));
    //$('#comparison a').attr('href', '/compare/?request='+ encodeURI(request));

$.get('/service/request/').then(function (successResponse) {

}, function (errorResponse) {

        console.log("errorResponse", errorResponse)
});

})();