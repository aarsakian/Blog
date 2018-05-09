'user strict';
var $ = require('jquery');
require('bootstrap-3-typeahead');

$(document).ready(function() {



     var actify=function (url){

        $('.nav-item').each(function(){
	    $(this).removeClass('active');
            var link=$(this).children().first()[0].pathname;

            if (url===link){
                $(this).addClass('active');}

            });
      }


   var  url=location.pathname;
   actify(url);



   
    var map = {}
    $('.typeahead').typeahead({
        minLength: 3,
        order: "asc",
        updater: function(item) {
            return item;
        },
   
    source: function (query,process) {

          $.get('/search', { query:query}, function (data) {
            var titlesbodies = [];
            $.each(data.data, function (i, post) {
               titlesbodies.push(post.body);
               titlesbodies.push(post.title);
               map[post.title] = post;
               map[post.body]= post;
           });
              process(titlesbodies);
             
        });
   },
   afterSelect: function(item){
     var post = map[item];
     if (typeof post !== "undefined") 
       window.location =  "/"+post.category+"/"+post.year+"/"+post.month+"/"+post.title;
     } 
  
  });




});