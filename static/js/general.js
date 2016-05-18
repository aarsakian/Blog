$(function(){
      
      var  converter = new Showdown.converter();
      $('.article').each(function(){
          $(this).html(converter.makeHtml($(this).text()));
      });
      
      var actify=function (url){
    
         $('.nav-pills li').each(function(){
	    $(this).removeClass('active');
            var link=$(this).children().first()[0].pathname;
           
            if (url===link){
                $(this).addClass('active');}
               
            });
         }
            
   
    
    
   var  url=location.pathname;
   actify(url);
   
   
    (function() {
        var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
        po.src = 'https://apis.google.com/js/plusone.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
      })();
  // $.getScript("//platform.twitter.com/widgets.js");
   
   
    $('.typeahead').typeahead({
    minLength:3,
    updater: function(item) {
        return item;
    },
   
    source: function (query,process) {
        return $.get('/search', { query:query}, function (data) {
            titlesbodies = [];
            $.each(data.data, function (i, post) {
               titlesbodies.push(post.body);
            });
              process(titlesbodies);
        });
    }
   afterSelect: function(item){
    $("#searchform").submit();
  } 
  
   });
   
   
})
