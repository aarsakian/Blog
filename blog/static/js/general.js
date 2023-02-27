'user strict';


document.addEventListener('load', function(){
  var  url=location.pathname;
  actify(url);

  const el = document.getElementsByClassName("aggregate").getElementsByClassName("answer-choice");
  let answerEl = {};
  el.addEventListener("click", (e) =>{
    if (!isObjectEmpty(answerEl)) {
      answerEl.parentNode.parentNode.classList.remove(["bg-success", "bg-danger"]);
    } else {
      answerEl.parentNode.parentNode.parentNode.parentNode.nextSibling.clasList.remove('disabled');
    }
 
  });

  const filePostFormEl = document.getElementById("#files-post-form")

  filePostFormEl.addEventListener("submit", (e) =>{
    e.preventDefault();
    const csrf_token = $(this).children().first();
    const formData = new FormData(filePostFormEl);
    const files = filePostFormEl.getElementsByTagName("input").files 
    files.forEach((file, idx) => {
      formData.append("file"+idx, file);
    })
    
  });


})


const isObjectEmpty = (objectName) => {
  return Object.keys(objectName).length === 0
}


function actify(url) {
  const navitems = Array.from(document.getElementsByClassName('.nav-item'));
  navitems.forEach(navitem => {
    navitem.classList.remove('active');
    let link = navitem.firstChild.pathname; 
    if (url === link) {
      navitem.classList.add('active');

    }
  });

  
}



/*$(document).ready(function() {




  $("body").on('submit',"#files-post-form", function(event){
    event.preventDefault();
    var csrf_token = $(this).children().first();
    var formData = new FormData($("#files-post-form")[0]);

    $.each($("#files-post-form input")[0].files, function(idx, file){
        formData.append("file"+idx, file);
    })
    $.ajax({
      type:'POST',
      url:'/upload',
      processData: false,
      contentType: false,
      async: false,
      cache: false,
      data : formData,
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
       post.year = post.timestamp.split(" ")[3];
       post.month = post.timestamp.split(" ")[2];
       var url = window.location.origin;
       url = url + "/articles/"+post.category+"/"+post.year+"/"+post.month+"/"+post.title
       window.location.href = url;

     } 
  
  });



});
*/
