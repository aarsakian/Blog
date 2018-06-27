'user strict';
var $ = require('jquery');
var _ = require('underscore');
require('bootstrap-3-typeahead');
require('bootstrap-notify');
var marked = require('marked');
var renderer = require('marked-forms')(new marked.Renderer());
//var markdown = function(txt) { return marked(txt, {renderer:renderer}); }



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

  $("#ga-accept").on( "click", function() {
        $.post('/ga-accept',  function(data){

        });
  });

   $("#ga-decline").on( "click", function() {
        $.post('/ga-decline',  function(data){

        });
  })


    var answerEl = {};

    $('.aggregate .answer-choice').on("click", function(){
         if (!_.isEmpty(answerEl)) {
             answerEl.parent().parent().removeClass("bg-success").removeClass("bg-danger");
         }
           answerEl = $(this);
           answerEl.parent().parent().parent().parent().next().removeClass('disabled');


     });

  $("body").on('submit',"#files-post-form", function(event){
    event.preventDefault();
    var csrf_token = $(this).children().first();
    var form_data = $('#files-post-form input').prop('files');
    $.ajax({
      type:'POST',
      url:'/upload',
      processData: false,
      contentType: false,
      async: false,
      cache: false,
      data : form_data,
      success: function(response){

      },
      headers:
      {
            'X-CSRF-TOKEN': csrf_token
      }
    });
  });


  $(".aggregate .submit").on("click", function(event){
     event.preventDefault();

     var title = $(this).parent().data("title");
     var url = '/api/answers/'+title;
     var p_answer = answerEl.data("answer");
     var data = JSON.stringify({p_answer:p_answer,is_correct:"True" });
     var csrf_token = $(this).prev().prev().val();


     $.ajax({
		url : url,
		type: "post",
		data: data,
		dataType:  "json",
		contentType: "application/json",
		success: highlightResult,
		headers:
        {
            'X-CSRF-TOKEN': csrf_token
        }
	  });

  })

  function highlightResult(data) {

       if (_.has(data, 'result')) {
            var result = data.result;
            changeColor(result);

            if (result) {

               $.notify({
	        // options
	            message: 'You found it.'
                },{
	            // settings
	            type:'success'
	            });

            }
        }

        if (data.remaining_attempts == 0 && !data.result) {
         $.notify({
	        // options
	            message: 'you can retry if you know how http works -)'
            },{
	            // settings
	            type:'info'
	        });
        }

        if (_.has(data, 'msg')) {
            $.notify({
	        // options
	            message: data.msg
            },{
	            // settings
	            type: function(){
	                if (data.remaining_attempts != 0)
	                   return 'warning';
	                else
	                    return 'danger';

	            }
            });
        }





   }

   function changeColor(result) {
       var colorResult = ""
       if (result) {
         colorResult = "bg-success";

       } else {
         colorResult = "bg-danger";
       }
       answerEl.parent().parent().addClass(colorResult);

  }


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


$(function () {
   var markdown = $('.article').text()
  var html = marked(markdown, {renderer:renderer});

});