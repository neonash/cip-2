(function(){
    $('#parent').removeClass('hidden');
    $('#parent').addClass('active');

    $('.selectpicker').selectpicker({
        size: 4
    });

    $('.selectpicker').selectpicker('selectAll');

    var query = window.urlUtils.getQueryParameter(window.location.href, 'request');
    var flag;
    console.log(query);

    $('#summary a').attr('href', '/summary/?request='+ encodeURI(query))
    $('#requestTopic a').attr('href', '/topicmodeling/?request='+ encodeURI(query))
    $('#analysis a').attr('href', '/analysis/?request='+ encodeURI(query))
    $('#clustering a').attr('href', '/clustering/?request='+ encodeURI(query))
    $('#comparison a').attr('href', '/compare/?request='+ encodeURI(query))

})();
