'user strict';

function highlightResult(data) {

  if (data.hasOwnProperty('result')) {
    const result = data.result;
    changeColor(result);

    if (result) {

          /*     $.notify({
	        // options
	            message: 'You found it.'
                },{
	            // settings
	            type:'success'
	            });
          */
            }
  }

  if (data.remaining_attempts == 0 && !data.result) {
       /*  $.notify({
	        // options
	            message: 'you can retry if you know how http works -)'
            },{
	            // settings
	            type:'info'
	        });*/
        }

   if (data.hasOwnProperty('msg')) {
        /*    $.notify({
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
            });*/
    }

  }


document.addEventListener('load', function(){
  var  url=location.pathname;
  actify(url);

  const el = document.getElementsByClassName("aggregate").getElementsByClassName("answer-choice");
  let answerEl = {};
  el.addEventListener("click", (e) =>{
    if (!isObjectEmpty(answerEl)) {
      answerEl.parentNode.parentNode.classList.remove(["bg-success", "bg-danger"]);
    } else {
      answerEl = e.target; 
    }
    answerEl.parentNode.parentNode.parentNode.parentNode.nextSibling.clasList.remove('disabled');
    
 
  });

  const filePostFormEl = document.getElementById("#files-post-form")

  filePostFormEl.addEventListener("submit", (e) =>{
    e.preventDefault();
    const csrf_token = $(this).children().first();
    const formData = new FormData(filePostFormEl);
    const files = filePostFormEl.getElementsByTagName("input").files 
    files.forEach((file, idx) => {
      formData.append("file"+idx, file);
    });
    
  });


  const submitAnswersEl = document.getElementsByClassName('aggregate').getElementsByClassName('submit');
  submitAnswersEl.addEventListener("click", (e) => {
    e.preventDefault();
    const title = e.parentNode.dataset.title;
    const url = new this.URL(`/api/answers/${title}`);
    const p_answer = answerEl.dataset.answer;
    const csrf_token = e.previousSibling.previousSibling.nodevalue;

    const headers = new Headers();
    headers.append('X-CSRF-TOKEN', csrf_token);
    const data = JSON.stringify({p_answer:p_answer,is_correct:"True" });
    fetch(url, {headers:headers, body:data}).then
      (response => response.json()).then
      (data => highlightResult(data));
      
  });

   




  const isObjectEmpty = (objectName) => {
      return Object.keys(objectName).length === 0
  }

  function changeColor(result) {
    let colorResult = ""
    if (result) {
      colorResult = "bg-success";
  
      } else {
        colorResult = "bg-danger";
      }
         answerEl.parentNode.parentNode.classList.add(colorResult);
  
    }

});

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





 




/*
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
*/




