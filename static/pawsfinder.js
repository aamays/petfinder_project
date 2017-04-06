"use strict"

$(document).ready(function(){

//THIS IS THE CODE FOR EXECUTING THE LOGIN
//event listener to login form
$("#login-form").submit(doLogin);
  // event handler function
  function doLogin(evt) {
      //keep the form from going to a new page
      evt.preventDefault();
      //get the form values
      var email = $("#email-field").val();
      var password = $("#password-field").val();

      //pack up the form values into an object
      var formData = {"email": email,
                      "password": password};

      //make the AJAX request
      $.post("/login.json", formData, function(results){
            console.log("results: ", results);
            var success = results.success;
            
            if (success === true) {
                //change message to show logged in status
                $("#logged-in-status").html("Welcome " + results.firstname + " you are logged in!");
                //hide login form
                $("#login-form").hide();
                $("#logout-button").removeAttr("hidden");
            }
            else {    
                $("#logged-in-status").html(results.message);
            }
        } //end of callback function
      ); //end of AJAX request
}; //end of doLogin function


//THIS IS THE CODE FOR EXECUTING THE LOGOUT
//attach event listener to execute logout
$("#logout-button").click(doLogout);
  //event handler
  function doLogout(evt) {
      //keep the form from going to a new page  
      evt.preventDefault();

      //make the AJAX request
      $.get("/logout.json", function(results){
            console.log("results: ", results);
            var success = results.success;
            
            if (success === true) {
                //change message to show logged out status
                console.log(results.message)
                $("#logged-in-status").html(results.message);
                $("#login-form").show();
                $("#logout-button").hide();
            }
        } //end of callback function
      ); //end of AJAX request
  }; //end of logout function

//THIS CODE IS FOR HIDING OR SHOWING THE BREEDS DROPDOWN
    $("#cats").hide(); // hide this when the page loads
  $("#animal-type").on("change", function() {
        if ($("#animal-type").find(":selected").text() !== "dog") {
              $("#dogs").hide();
              $("#cats").show();
      } else {
              $("#cats").hide();
              $("#dogs").show();
      }

  });

 });//end of document ready function