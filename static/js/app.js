/* Your custom JavaScript here */
(function(){
   window.app = {};
   app.collections = {};
   app.models = {};
   app.views = {};
   app.mixins = {};
   app.routes={};
   $(function(){
      
      
      
      
    
     
    
         

     
      //if ($('#bd').width()<900){
      //   var rightmargin=$(window).width()-$('#bd').offset().left-$('#bd').width();
      //   $('#nav li ul').css({'width': $('#bd').width()-rightmargin/8+2});
      //}
      //else
      // $('#nav li ul').css({'width': $('#bd').width()-5});
      //
      //$(window).resize(function() {
      //     
      //      $('#nav li ul').css({'width': $('#bd').width()-5});
      //        $('#right').removeClass('fixed');
      //});
//    console.log(top);

//      var top = $('#right').offset().top - parseFloat($('#right').css('marginTop').replace(/auto/, 0));
//     
//      $(window).scroll(function (event) {
//	// what the y position of the scroll is
//	      var y = $(this).scrollTop();
//         $height=$('#right').height();
//       
//	// whether that's below the form
//	if (y >= top) {
//	  // if so, ad the fixed class
//	  $('#right').addClass('fixed');
//       
//         $('#right').css({'left':$('#left').width()+$('#left').offset().left+20});//left div+offset
//         $('#right').width($('#bd').width()-20-$('#left').width());//bd-left dev -margin
//        
//        
//	} else {
//	  // otherwise remove it
//	  $('#right').removeClass('fixed');
//             $('#right').css({'left':'64%'});//left div+offset
//         $('#right').width('24%');//bd-left dev -margin
//      
//	}
//      });
   
    


    
 
   

    /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
         // required: replace example with your forum shortname
  // $(document).on("mouseenter",'span.backlink a',function(){
  //      $(this).children().each(function(){
  //          $container=$(this);
  //          $container.attr('src','/static/images/arrow_black_left_16x16.png');
  //       });
  //                        
  // });
  //$(document).on("mouseleave",'span.backlink a',function(){
  //      $(this).children().each(function(){
  //          $container=$(this);
  //          $container.attr('src','/static/images/arrow_left_16x16.png');
  //       });
  //                        
  // });
  // 
   // var disqus_shortname = 'myblogaa';
  //  var disqus_identifier = '1';
    // var disqus_url = 'http://127.0.0.1:8082/#!/machine_learning/1';
   // var disqus_developer = '0';
   // var editevent=false;
    /* * * DON'T EDIT BELOW THIS LINE * * */
//    var disqview=function() {
//       if (runonce)   {
//        console.log('test');
//       //var disqus_identifier=1;
//	//var disqus_url='http://127.0.0.1:8082/#!/machine_learning/1';
////	var disqus_title='tes';
//        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
//        dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
//        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
//       }
//    };
//
//
//       var reset = function(disqconf){
//	if ((typeof DISQUS !== 'undefined' ) && (app.Posts.length==1)) {
//            
//   DISQUS.reset({
//      reload: true,
//      config: function () {
//	console.log(this);
//        this.page.identifier = disqconf.id;
//        this.page.url = 'http://aarsakian.appspot.com/#!/machine_learning/'+disqconf.id;
//        this.page.title = disqconf.title;
//      }
//      
//    });
//        }
//   };


    

    var ENTER_KEY=13;
  

    var Tag=new app.models.Tag();
   

     
   app.models.User=new app.models.User();

   app.views.Main = Backbone.View.extend({

        el: $("#bd"),
        user: app.models.User,
        template :Handlebars.compile($("#collection-template").html()),
        newposttemplate:Handlebars.compile($("#new-post-template").html()),
         initialize: function() {
       
            $(this.el).undelegate('#submit', 'click');
             this.views=[]
         //    this.user.fetch();
             this.user.fetch({success: function(model,response){
              
                  this.changed=true;
                    model.set({"user_status":response});
                    
                }});
                this.user.on('change:user_status', function(model, color) {
                    //  console.log(this.options.url);
                 });
         
               $('#bd').show();
            
                 if (this.options.category){//a particular category
                      
                     app.Posts=new app.collections.Posts([],{"category":this.options.category});
                   
                     actify("categories");
                  }
                  else if (this.options.tag){//a particular tag
                     app.Posts=new app.collections.Posts([],{"tag":this.options.tag});
                  
                     actify("tags");
                  
                  }
		 
                 else if (this.options.postkey){// a post
                        app.Posts=new app.collections.Posts([],{"postkey":this.options.postkey});
                 }
                    else if (this.options.url==='tags') {//a tag view
                        actify("tags");
                        app.Posts=new app.collections.Tags([],{"url":this.options.url});
                        app.Posts.header="Tags";
                     
                     }
                      else if (this.options.url==='about') {//a tag view
                        actify("about");   
                       app.Posts=new app.collections.Posts([],{"about":this.options.url});
                       app.Posts.header="Edit Mode";
                        
                     
                     }
                     else if (this.options.url==='categories'){
                        actify("categories")
                        app.Posts=new app.collections.Categories([],{"url":this.options.url});
                      
                        app.Posts.header="Categories";
                     }
                    else if (this.options.postTitle) {
                       app.Posts=new app.collections.Posts([],{"postTitle":this.options.postTitle});
                       
                     }
              
                  else{//index page
                     console.log('central index');
                     app.Posts=new app.collections.Posts();
                     app.Posts.header="All Posts";
                  }
               
                  app.Posts.on('reset', this.render, this);
                  app.Posts.on('add', this.render, this);
                  app.Posts.fetch();  
                  		  
		
		},
        
         events:{
             "click #submit"  : "createNewPost",
             "keypress #newpost input"  :    "doNothing",
            
            
         },
	
         render:function(){
                console.log(app.Posts);
                this.$("#posts").html('');
                this.$("#tags ul").html('');
                this.$("#categories ul").html('');
           
        
           
                 //app.Posts.header=_.filter(app.Posts.dataheader,function(val,key){
                 //   
                 //     if (key===app.Posts.category)
                 //    
                 //         return val
                 //     
                 //  });
               //else if (typeof app.Posts.header!="undefined") 
               //   app.Posts.header=app.Posts.header;
               //else if (typeof app.Posts.type!="undefined")
               //    app.Posts.header=app.Posts.dataheader;
              
                 
		context={title:app.Posts.header,type:app.Posts.type}
                app.Posts.user_status=this.user.toJSON().user_status;
                //if (app.Posts.user_status.user_status)
                //  window.location=app.Posts.url+"#editmode";
                  
		newpostcontext={user_admin:this.user.toJSON().user_status.user_status}
		$el=$(this.el);
                $el.find("#newpost").empty('');
                $el.find("#newpost").append(this.newposttemplate(newpostcontext));
		$el.find('h2').remove();
		$el.find('.page-header').prepend(this.template(context));
             
                  app.Posts.each(this.addOne, this);
                 
             
            
         },
         addOne:function(modelpost){
         
            if (app.Posts.type==="tags"){
               console.log('tags');
               view=new app.views.Tag({model:modelpost});//this need the parse specification of json
               $("#taglist").append(view.render().el);
               this.views.push(view);
            }
            else if (app.Posts.type==="categories"){
               console.log('cats');                          
               view=new app.views.Category({model:modelpost});//this need the parse specification of json
               $("#categorylist").append(view.render().el);
               this.views.push(view);
            }
            else  if (this.options.category==="about"){
                view=new app.views.About({model:modelpost});
               $("#posts").append(view.render().el);
             
            }
            else{
               view =new app.views.Post({model:modelpost});
               this.views.push(view);
               $("#posts").append(view.render().el);
             }
          
	    
	 },
         doNothing:function(e){
        //     console.log('nothing');
             if ( e.keyCode === ENTER_KEY )
               return false
            return 
         },
        
         createNewPost:function(){
         
         //if (app.Posts.length==1){
          //       app.Posts.url='/posts/'+ this.options.category;
          //       window.siterouting.navigate('!/'+ this.options.category);
                // window.App=new AppView({"category":this.options.category});
            //}  
            
               
               //_.each(this.views,function(view){
               //       console.log($(view.el));
               //        view.model.unbind("change", view .render);
               //       view.undelegateEvents();});//clear all views
               this.body = $(this.el).find("#new-post-body");
               this.title=$(this.el).find("#new-post-title");
               this.tags=$(this.el).find("#new-post-tag");
               this.category=$(this.el).find("#new-post-category");
               
                console.log(this.tags);
           
        //     editevent=true;

            console.log(this.tags.val().split(','));
            app.Posts.create({title:this.title.val(),body:this.body.val(),category:this.category.val(),
                              tags:this.tags.val().split(',')});//add event
      
            this.$("#new-post-body").val('');
            this.$('#new-post-tag').val('');
            this.$("#new-post-title").val('');
            this.$("#new-post-category").val('');
            this.unbind();


            
            return false;
          
         }
	 

     
        
    });
    
    
   

    
    
     var runonce=true
    //  disqview();
    // $('#disqus_thread').hide();
     window.siterouting=new  app.routes.Main;
     Backbone.history.start({pushState: true});

    $("#editabout a").on("click",function(){
       var  url=location.pathname.substring(1);
        window.App=new app.views.Main({"url":url});
      });
  
  
   
   
  });

})();
