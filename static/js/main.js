document.getElementById("loginbutton").addEventListener("click", function(event){
//function validateAndLoadHomePage(){
    event.preventDefault();
    var username = document.getElementById('username_id').value;
    var password = document.getElementById('password_id').value;
    console.log(username);
    console.log(password);
    //if(username === 'root' && password === 'rootpass'){
        //alert("login successful");
        //var formdata = new FormData(this);
    var usernameAndPassword = {};
    usernameAndPassword['username'] = username;
    usernameAndPassword['password'] = password;
    $.ajax({
        url: '/ba/homepage/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(usernameAndPassword)
    }).done(function(data){
        //event.preventDefault();
        loginIndicator = data['indicator'];
        console.log('reached');
        console.log(data);
        console.log(loginIndicator);
        if (loginIndicator === 'success'){
            alert("Logged in sucessfully");
            console.log('in login if');
            var Indicator = {};
            Indicator['indicator'] = loginIndicator;
            $.ajax({
                url: '/ba/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(Indicator)
            }).done(function(innerdata){
                loginInnerIndicator = innerdata['ind'];
                var loginInnerIndicatorObject = {};
                loginInnerIndicatorObject['ind'] = loginInnerIndicator;
                if (loginInnerIndicator === 'success'){
                    /*$.ajax({
                        url: '/ba/loadHomePage/',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(loginInnerIndicatorObject)
                    });*/
                    window.location.href = "/ba/loadHomePage/";
                }
            }).fail(function(xhr){
                try {
                    var msg = $.parseJSON(xhr.responseText);
                    $("#error_msg").text(msg.message);
                    $("#error_dialog").css("display", "block");
                }catch(e){
                    $("#error_msg").text("Failed to login !!" + e);
                    $("#error_dialog").css("display", "block");
                }
            });
            //window.location.href = "/ba/";
        }else{
            alert("Please try again..");
            console.log('in login else');
            window.location.href = "/";
        }
        //console.log("just before ba");
        //window.location.href = "/ba/";
    }).fail(function(xhr){
        try {
            var msg = $.parseJSON(xhr.responseText);
            $("#error_msg").text(msg.message);
            $("#error_dialog").css("display", "block");
        } catch(e) {
            $("#error_msg").text("Failed to login !!" + e);
            $("#error_dialog").css("display", "block");
        }
    });
    //}else{
     //   alert("Incorrect username or password. Please try again!!");
    //}
});
    /*$('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });*/

    /*function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }*/
