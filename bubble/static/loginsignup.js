$(document).ready(function(){
    $(".l_s_message_cross_text").click(function(){
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
    });
    
    $(".l_s_form_signin_forgot_password").click(function(){
        if(!$(".l_s_singup").hasClass("l_s_singup_toggle")){
            $(".l_s_form_signup_password_wrap").hide();
            $(".l_s_form_signup_password2_wrap").hide();
            $(".l_s_form_signup_button_signup").html("Reset");
            $('[name=sigup_username_countrycode]').removeAttr('disabled');
            $('[name=sigup_username]').removeAttr('disabled');
            $(".l_s_singup").html("Forget Password");
            $('[name=resetPassword]').val("yes");
            $(".l_s_bg").css("background","#FFF2F2");
            $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
            $(".l_s_message_content").text("");
            $(".l_s_form_signup").css({display:"block"});
            $(".l_s_form_signin").css({display:"none"});
            $(".l_s_singup").addClass("l_s_singup_toggle");
            $(".l_s_singin").addClass("l_s_singin_toggle");
            $('.clr_signin').val('');
            $('.clr_signup').val('');
        }
    });
    $(".l_s_singup").click(function(){
        if(!$(".l_s_singup").hasClass("l_s_singup_toggle")){
            $(".l_s_form_signup_password_wrap").hide();
            $(".l_s_form_signup_password2_wrap").hide();
            $('[name=sigup_username_countrycode]').removeAttr('disabled');
            $('[name=sigup_username]').removeAttr('disabled');
            $(".l_s_bg").css("background","#FFF2F2");
            $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
            $(".l_s_message_content").text("");
            $(".l_s_form_signup").css({display:"block"});
            $(".l_s_form_signin").css({display:"none"});
            $(".l_s_singup").addClass("l_s_singup_toggle");
            $(".l_s_singin").addClass("l_s_singin_toggle");
            $('.clr_signin').val('');
            $('.clr_signup').val('');
        }
    });
    $(".l_s_singin").click(function(){
        if($(".l_s_singin").hasClass("l_s_singin_toggle")){
            //$("#recaptcha-container").show();
            $(".l_s_form_signup_sendotp_button").show();
            $(".l_s_form_signup_otpenter_wrap").hide();
            $(".l_s_form_signup_button_signup").css("visibility","hidden");
            $(".l_s_form_signup_password_wrap").hide();
            $(".l_s_form_signup_password2_wrap").hide();
            $('[name=sigup_username_countrycode]').removeAttr('disabled');
            $('[name=sigup_username]').removeAttr('disabled');
            $(".l_s_singup").html("Sign Up");
            $('[name=resetPassword]').val("no");
            $(".l_s_form_signup_button_signup").html("Sign Up");
            $(".l_s_bg").css("background","#F2FFF2")
            $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
            $(".l_s_message_content").text("");
            $(".l_s_form_signup").css({display:"none"});
            $(".l_s_form_signin").css({display:"block"});
            $(".l_s_singin").removeClass("l_s_singin_toggle");
            $(".l_s_singup").removeClass("l_s_singup_toggle");
            $('.clr_signin').val('');
            $('.clr_signup').val('');
        }
    });

    $('#signin_form_id').submit(function(event) {
        event.preventDefault();
        $(".lbg").show();
        var formData = $(this).serialize();
        $.ajax({
            type: 'POST',
            url: signinurl, // Replace 'your_url_name' with the actual URL name
            data: formData,
            success: function(response) {
                showalert(response.message.text,"l_s_should_"+response.message.color_code);
                $('.clr_signin').val('');
                $('.clr_signup').val('');
                $(".lbg").hide();
                
                if(response.message.color_code==="success"){
                    setTimeout(function() {
                        location.reload(true);
                       }, 1000);
                    
                }
            },
            error: function(xhr, status, error) {
                showalert("unknown Error occured please try again","l_s_should_danger");
                $(".lbg").hide();
                console.error(xhr.responseText);
            }
        });
    });

    $(".l_s_form_button_cancel").click(function(){
        $(".l_s_singin").click();
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
        $(".l_s_wrap").css({display:"none"});
    });
    $('.l_s_wrap').on('click', function(e) {
        /*if (e.target !== this)
          return;
        $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
        $(".l_s_message_content").text("");
        $(".l_s_wrap").css({display:"none"});
        */
      });


      

$(".l_s_form_signup_sendotp_button").click(function(){
    var countrycode=$('[name=sigup_username_countrycode]').val();
    var mobilenumber=$('[name=sigup_username]').val();
    var resetPassword=$('[name=resetPassword]').val();
    var countryCodeRegex = /^\+\d{1,3}$/; // Regex for country code
    var mobileNumberRegex = /^\d{10}$/; // Regex for 10 digit mobile number
    var phoneNumber =(countrycode+mobilenumber).trim();

    if (!countryCodeRegex.test(countrycode)) {
        showalert("invalid country code","l_s_should_danger");
    } else if (!mobileNumberRegex.test(mobilenumber)) {
        showalert("invalid mobile number","l_s_should_danger");
    }else{
    $(".lbg").show();
    fetch('checkUser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToen
        },
        body: JSON.stringify({'phoneNumber': phoneNumber,'resetPassword':resetPassword})
    })
    .then(response => response.json())
    .then(data =>  {
        $(".lbg").hide();
        if(data.status === "otpVerified"){
            showalert("Phone number already verified successfully!","l_s_should_success");
            $('[name=sigup_username_countrycode]').attr('disabled',true);
            $('[name=sigup_username]').attr('disabled',true);
            $(".l_s_form_signup_sendotp_button").hide();
            $(".l_s_form_signup_button_signup").css("visibility","visible");
            $(".l_s_form_signup_otpenter_wrap").hide();
            $(".l_s_form_signup_password_wrap").show();
            $(".l_s_form_signup_password2_wrap").show();
        }else if(data.status === "exist"){
        showalert("mobile number already exist","l_s_should_danger");
        }else if(data.status === "notExist" || data.status === "reset"){
            var appVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container');
            firebase.auth().signInWithPhoneNumber(phoneNumber, appVerifier)
                .then(function (confirmationResult) {
                    window.confirmationResult = confirmationResult;
                    showalert("otp sent please enter otp below","l_s_should_success");
                    $('[name=sigup_username_countrycode]').attr('disabled',true);
                    $('[name=sigup_username]').attr('disabled',true);
                    $(".l_s_form_signup_otpenter_wrap").show();
                    $(".l_s_form_signup_sendotp_button").hide();
                    $("#recaptcha-container").html("");
                }).catch(function (error) {
                    console.log(error);
                    showalert("some exception occured","l_s_message_wrap");
                });
        }else{
        showalert("unknown error at send otp","l_s_should_danger");
        }
    })
    .catch(error => {
        $(".lbg").hide();
        console.log(error);
        showalert("unknown error","l_s_should_danger");
    });

    }
});

$(".l_s_form_signup_submitotp_button").click(function(){
    var otp = $('[name=firebase_otp]').val();
    $(".lbg").show();
    window.confirmationResult.confirm(otp).then(function (result) {
        var user = result.user;
        user.getIdToken().then(function(idToken) {
            fetch('/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToen
                },
                body: JSON.stringify({otp: idToken})
            }).then(response => response.json())
              .then(data => {
                $(".lbg").hide();
                  if(data.status === "success" || data.status === "reset") {
                    showalert("Phone number verified successfully!","l_s_should_success");
                    $(".l_s_form_signup_button_signup").css("visibility","visible");
                    $(".l_s_form_signup_otpenter_wrap").hide();
                    $(".l_s_form_signup_password_wrap").show();
                    $(".l_s_form_signup_password2_wrap").show();
                  } else if(data.status === "exist"){
                    showalert("phone number already exist","l_s_should_danger");
                  }else {
                    showalert("some exception occured","l_s_should_danger");
                    console.log("Verification failed: " + data.message);
                  }
              }).catch(error => console.log(error));
        });
    }).catch(function (error) {
        $(".lbg").hide();
        console.log(error);
        showalert("Invalid OTP!","l_s_should_danger");
    });
});
$(".l_s_form_signup_button_signup").click(function(){
    $('#signup_form_id').submit();
});
$('#signup_form_id').submit(function(event) {
    event.preventDefault();
    $(".lbg").show();
    var formData = $(this).serialize();
    $.ajax({
        type: 'POST',
        url: signupurl, // Replace 'your_url_name' with the actual URL name
        data: formData,
        success: function(response) {
            if(response.message.color_code==="success"){
                $(".l_s_singin").click();
                /*$(".l_s_form_signup").css({display:"none"});
                $(".l_s_form_signin").css({display:"block"});
                $(".l_s_singin").removeClass("l_s_singin_toggle");
                $(".l_s_singup").removeClass("l_s_singup_toggle");
                $(".l_s_singup").html("Sign Up");
                $('[name=resetPassword]').val("no");
                $('.clr_signin').val('');
                $('.clr_signup').val('');*/
            }
            showalert(response.message.text,"l_s_should_"+response.message.color_code);
            $(".lbg").hide();
        },
        error: function(xhr, status, error) {
            showalert("unknown Error occured please try again","l_s_should_danger");
            $(".lbg").hide();
            console.error(xhr.responseText);
        }
    });
});
function showalert(message,classname){
    $(".l_s_message_wrap").attr('class', 'l_s_message_wrap');
    $(".l_s_message_wrap").addClass(classname);
    $(".l_s_message_content").text(message);
}
});