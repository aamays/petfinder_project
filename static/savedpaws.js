"use strict"

$(document).ready(function(){

//THIS IS THE CODE FOR SHOWING THE SEARCH FORM
$("#save-search-form").hide();
$("#save-box").change(function(){
    if ($("#save-box").is(":checked")) {
      $("#save-search-form").show();
    } else {
      $("#save-search-form").hide();
    } 
});

//THIS IS THE CODE FOR SAVING A SEARCH
$("#save-search-button").click(function(evt){
   evt.preventDefault();
   saveSearch();
  });
//event listener for saveSearch
function saveSearch(evt) {
    
    //get the form values
    var title = $("#saved-title").val();
    var description = $("#saved-description").val();
    var saveBox = $("#save-status").val();

    //pack up the form values into an object
    var formData = {"title": title,
                    "description": description,
                     "save": saveBox};

    //make the AJAX request
    $.post("/save-search.json", formData, function(results){
          console.log("results: ", results);
          var success = results.success;

          if (success === true) { 
          $("#save-status").html(results.message);
         } 
      } //end of callback function
    ); //end of AJAX save search request
 }; //end of saveSearch function

//CODE FOR DISPLAYING THE SEARCH
//event listener
$("#saved-searches").on('click', function(){
 
    //make the AJAX request, event handler
    $.get("/get-saved-searches.json", function(results){
          console.log("results: ", results.results);
          
          for (var i = 0; i < results.results.length; i++){
            $("#saved-title").append("<p> Title: "+results.results[i].title 
                 + " &nbsp; Description: " + results.results[i].description + "</p>");
          }     
    });
  }); // end of event listener

//CODE FOR MODAL
//event listener for Modal
$("#saved-searches").on("click", function(){
  $("#save-modal").modal("show");



});


}); //end of document ready function