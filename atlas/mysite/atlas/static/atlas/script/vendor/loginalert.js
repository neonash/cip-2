  $(document).ready(function(){
        $('.log-btn').click(function(){
          var un = document.getElementById("UserName").value;
          var pw = document.getElementById("PassWord").value;
          //alert(un);
          if(un != "user1" || pw != "1234")
          {
              $('.log-status').addClass('wrong-entry');
              $('.alert').fadeIn(500);
              setTimeout( "$('.alert').fadeOut(1500);",3000 );
              $('.form-control').keypress(function(){
                  $('.log-status').removeClass('wrong-entry');
              });
          }
          else
          {
              parent.location='ATLAS_Home.html';
          }
        });
    });