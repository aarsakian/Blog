(function(){      
      app.routes.Main= Backbone.Router.extend({
         

        
        routes: {
         
            "":                   "main",
          
           ":entity":     "displayPosts"
      
          
          
          
        },
        main: function(){
          var  url=location.pathname.substring(1);
              //app.models.User.fetch({success: function(model,response){
              //     
              //      model.set("user_status",response);
              //  }});
              console.log(url);
              //
            
            if ((url) &&  (url.split('/').length===1) && (url!="about"))
                  window.App=new app.views.Main({"url":url});
           
                 
           //else if (url.split('/').length===2)
           // {   
           //       
           //       window.App=new app.views.Main({"postTitle":url.split('/')[1]});
           // }
            else if (!url) //index page
            {   
            
                  window.App=new app.views.Main();
            }
         
                     
         
        },
     
       
         
         displayPosts:function(entity){
              url=location.pathname.substring(1);//part after hash
              if (url=="categories")   
                     window.App=new app.views.Main({"category":entity});
              else if (url=="tags")
                     window.App=new app.views.Main({"tag":entity});
               else if (url=="edit"){
                     console.log('edit');
                     //window.App=new app.views.Main({"tag":entity});
               }
            
                     
           //     window.siterouting.navigate("!/"+category+"/"+id);
//	         (function(d,s,id){
//      
//          var js,fjs=d.getElementsByTagName(s)[0];
//	  if(!d.getElementById(id)){js=d.createElement(s);
//	  js.id=id;js.src="https://platform.twitter.com/widgets.js";
//	  fjs.parentNode.insertBefore(js,fjs);}})
//	  (document,"script","twitter-wjs");
//	
//          
//            window.___gcfg = {
//        lang: 'en-US'
//      };
//
//	    //console.log(  app.Posts.get(id));
//           if (typeof app.Posts!=="undefined"){
//              app.Posts.reset(app.Posts.get(id));
//              app.Posts.url="posts/"+category+"/"+id;
//           }
//            else
//              window.App=new app.views.Main({category:category,id:id});
//            // $.getScript("http://platform.twitter.com/widgets.js");
//	   
//          //  $('#disqus_thread').show();
//         },
//	 displayPostTag: function(tagid){
//            console.log('display a post');
//   
//               window.App=new app.views.Main({tagid:tagid});//actually a tag
//            
//	 },
//         
//         displayTags: function(){
//            window.App=new app.views.Main({tag:"tags"})
//            
         }

    });
})(app.routes);
