(function(){
    console.log("LOADING UPLOAD JS")
    //$('#helpbox').hide();


    $(document).on('ready', function() {

        function loadTable(){
            var table = document.getElementById("configTable");
            var r, c;
            for(r=0;r<15;r++){

                var row = table.insertRow(-1);
                for(c=0;c<2;c++){
                    var cell2 = row.insertCell(-1);
                    if (r == 0 && c == 0){
                        cell2.innerHTML = "Dimensions";
                    }
                    else if( r == 0 && c == 1){
                        cell2.innerHTML = "Levels";
                    }
                    else{
                        cell2.innerHTML = "cell";
                    }
                }
            }
        }

        //loadTable();

        $("#input-440").fileinput({
            uploadUrl: '/service/upload/',
            maxFilePreviewSize: 1024,
            showBrowse: true,
            allowedFileExtensions: ["txt", "csv", "text"],
            browseOnZoneClick: true,
            maxFileCount: 1
        });

//        $( "#input-440" ).promise().done(function() {
//            alert( " Finished! " );
//        });


//        $('//button:first[contains(@class,"kv-file-upload")]').on("click", function(){
//            console.log("kv file upload button clicked");
//            call_readdims();
//        });

//        $('//a[contains(@class,"fileinput-upload-button")]').on("click", function(){
//            console.log("file upload button clicked");
//            call_readdims();
//        });

        function call_readdims(){
            $.get('/service/readdims/').then(function (successResponse) {
                //console.log('Stringify successResponse', JSON.stringify(successResponse,null, 2));
                console.log('Parsed successResponse', JSON.parse(successResponse));

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
                        { name: "dimensions", type: "text", width: 100, title:"Dimensions" },
                        { name: "level1", type: "text", width: 150, title: "Level 1" },
                        { name: "level2", type: "text", width: 150, title: "Level 2" },
                        { name: "level3", type: "text", width: 150, title: "Level 3" },

                    ],
                    rowClick: function(args) {
                        // save selected item
                        selectedItem = args.item;

                        // save selected row
                        $selectedRow = $(args.event.target).closest("tr");

                        // add class to highlight row
                        $selectedRow.addClass("selected-row");
                        console.log(selectedItem);
                        console.log(selectedItem.reqKw);
                        //window.location = "../summary/?request=" + encodeURI(selectedItem.reqKw);
                    }
                });
                console.log("Done populating dim table");
            }, function (errorResponse) {
                    console.log("errorResponse", errorResponse)
            });
        }



        $("#input-441").fileinput({
            uploadUrl: '/service/upload/',
            maxFilePreviewSize: 1024,
            showBrowse: false,
            allowedFileExtensions: ["txt", "csv", "text"],
            browseOnZoneClick: true,
            maxFileCount: 1
        });
        $("#input-442").fileinput({
            uploadUrl: '/service/upload/',
            maxFilePreviewSize: 1024,
            showBrowse: false,
            allowedFileExtensions: ["txt", "csv", "text"],
            browseOnZoneClick: true,
            maxFileCount: 1
        });

        $("#input-44").fileinput({
            uploadUrl: '/service/upload/',
            maxFilePreviewSize: 1024,
            showBrowse: true,
            allowedFileExtensions: ["txt", "csv", "text"],
            browseOnZoneClick: true,
            maxFileCount: 1
        });

        $("input:checkbox[name='opt1']").change(function() {
            if(this.checked) {
                $('#sd_upload').show();
            }
            else{
                $('#sd_upload').hide();
            }
        });

        $("input:checkbox[name='opt2']").change(function() {
            if(this.checked) {
                $('#td_upload').show();
            }
            else{
                $('#td_upload').hide();
            }
        });

        var step1_choice, step2_choice = "";

        $('#btnNext0').on("click", function(){
            var x = document.getElementsByClassName("file-upload-indicator");
            try{
                if(x[0].title == "Uploaded" ) {
//                    alert(x[0].title);
                    //call_readdims();
                   $('#sd_panel').removeClass('hidden');
                    $('#tag_panel').addClass('hidden');
                }

                else {
                    alert("Please upload a file first!");
                }
            }
            catch(err){
            alert("Please upload a file first!");
            }

        });


        $('#btnNext1').on("click", function(){
//        console.log("inside button click 1");
            $('#td_panel').removeClass('hidden');
            $('#sd_panel').addClass('hidden');
        });

        $('#btnNext2').on("click", function(){
//                console.log("inside button click 2");

            $('#data_panel').removeClass('hidden');
            $('#td_panel').addClass('hidden');
        });

        $('#btnStart').on("click", function(){
            alert("Analysis initiated. You can track the progress as listed on the home page.");
            $.get('/service/start/').then(function (successResponse) {
                console.log('Parsed successResponse', JSON.parse(successResponse));
            }, function (errorResponse) {
                    console.log("errorResponse", errorResponse)
            });
            //window.location("127.0.0.1:8000/");
            location.href = "/";
        });

        $('#help').click(function(){
            $('#helpbox').toggle('swing');
        });

//        $( "#btnNext0" ).mousedown(function() {
//          alert( "Handler for .mousedown() called." );
//        });

    });



//    $('#fileupload').fileupload({
//        url: '/service/upload/',
//        dataType: 'json',
//        done: function (e, data) {
//            console.log("File uploaded");
//            if($('<p/>').text().length > 1){
//                $('<p/>').text("");
//            }
//            $('<p/>').text(data.files[0].name).appendTo('#files');
//        },
//        progressall: function (e, data) {
//            var progress = parseInt(data.loaded / data.total * 100, 10);
//            $('#progress .progress-bar').text(progress + '%');
//            $('#progress .progress-bar').css('width', progress + '%');
//        }
//    }).prop('disabled', !$.support.fileInput)
//        .parent().addClass($.support.fileInput ? undefined : 'disabled');

})();