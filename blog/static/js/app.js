var DefaultRouter = Backbone.Router.extend({
  routes: {
  
  },

  // Redirect to contacts app by default
  defaultRoute() {
    this.navigate('edit', true);
  }
});


var App = {
   Models: {},
   Collections: {},
   Routers: {},
   
  start() {
    // Initialize all available routes
    _.each(_.values(this.Routers), function(Router) {
      new Router();
    });

    // The common place where sub-applications will be showed
    App.mainRegion = new Region({el: '#bd'});

    // Create a global router to enable sub-applications to redirect to
    // other urls
    App.router = new DefaultRouter();
    Backbone.history.start({pushState: true});

  },
   
   
     // Only a subapplication can be running at once, destroy any
  // current running subapplication and start the asked one
  startSubApplication(SubApplication) {
    // Do not run the same subapplication twice
    if (this.currentSubapp && this.currentSubapp instanceof SubApplication) {
      return this.currentSubapp;
    }

    // Destroy any previous subapplication if we can
    if (this.currentSubapp && this.currentSubapp.destroy) {
      this.currentSubapp.destroy();
    }

    // Run subapplication
    this.currentSubapp = new SubApplication({region: App.mainRegion});
    return this.currentSubapp;
  },
  
  
}


//alterPostForm(){
     // $("form").submit(function(e){
       //  e.preventDefault();
      //});
//  }
//(function(){
//   window.app = {};
//   app.collections = {};
//   app.models = {};
//   app.views = {};
//   app.mixins = {};
//   app.routes={};
//   $(function(){
//    $("form").submit(function(e){
//        e.preventDefault();
//    });
//   
//   var ENTER_KEY=13;
//  
//   var Tag=new app.models.Tag();
//   
//   app.models.User=new app.models.User();
//
//   app.views.Main = Backbone.View.extend({
//      
//      el: $("#bd"),
//      user: app.models.User,
//      template :Handlebars.compile($("#collection-template").html()),
//      newposttemplate:$("#newpost").html(),
//      
//      initialize: function() {
//         
//         $(this.el).undelegate('form #submit', 'click');
//         this.views=[]
//        
//         this.user.fetch({success: function(model,response){
//              
//            this.changed=true;
//            model.set({"user_status":response});
//                    
//         }});
//                this.user.on('change:user_status', function(model, color) {
//                    //  console.log(this.options.url);
//                 });
//         
//         $('#bd').show();
//            
//         if (this.options.category){//a particular category
//                      
//                     app.Posts=new app.collections.Posts([],{"category":this.options.category});
//                   
//                     actify("categories");
//         }
//         else if (this.options.tag){//a particular tag
//                     app.Posts=new app.collections.Posts([],{"tag":this.options.tag});
//                  
//                     actify("tags");
//                  
//         }
//		 
//         else if (this.options.postkey){// a post
//                        app.Posts=new app.collections.Posts([],{"postkey":this.options.postkey});
//         }
//         else if (this.options.url==='tags') {//a tag view
//                        actify("tags");
//                        app.Posts=new app.collections.Tags([],{"url":this.options.url});
//                        app.Posts.header="Tags";
//                     
//         }
//         else if (this.options.url==='about') {//a tag view
//                        actify("about");   
//                       app.Posts=new app.collections.Posts([],{"about":this.options.url});
//                       app.Posts.header="Edit Mode";
//                        
//                     
//         }
//         else if (this.options.url==='categories'){
//                        actify("categories")
//                        app.Posts=new app.collections.Categories([],{"url":this.options.url});
//                      
//                        app.Posts.header="Categories";
//         }
//         else if (this.options.postTitle) {
//                       app.Posts=new app.collections.Posts([],{"postTitle":this.options.postTitle});
//                       
//         }
//              
//         else{//index page
//                
//                     app.Posts=new app.collections.Posts();
//                    
//         }
//               
//         app.Posts.on('reset', this.render, this);
//         app.Posts.on('add', this.render, this);
//         app.Posts.fetch();
//         console.log("fetched "+app.Posts);
//                  		  
//		
//		},
//        
//         events:{
//            "click form #submit"  : "createNewPost",
//            "keypress #newpost input"  :    "doNothing",
//            "keypress form #new-post-tags"  :    "createNewPost"
//            
//            
//         },
//	
//         render:function(){
//            this.$("#posts").html('');
//            this.$("#tags ul").html('');
//            this.$("#categories ul").html('');
//           
//        
//           
//                 //app.Posts.header=_.filter(app.Posts.dataheader,function(val,key){
//                 //   
//                 //     if (key===app.Posts.category)
//                 //    
//                 //         return val
//                 //     
//                 //  });
//               //else if (typeof app.Posts.header!="undefined") 
//               //   app.Posts.header=app.Posts.header;
//               //else if (typeof app.Posts.type!="undefined")
//               //    app.Posts.header=app.Posts.dataheader;
//              
//                 
//		 context={title:app.Posts.header,type:app.Posts.type}
//                app.Posts.user_status=this.user.toJSON().user_status;
//                //if (app.Posts.user_status.user_status)
//                //  window.location=app.Posts.url+"#editmode";
//      
//		newpostcontext={user_admin:this.user.toJSON().user_status.user_status}
//		$el=$(this.el);
//              //  $el.find("#newpost").empty('');
//               // $el.find("#newpost").append(this.newposttemplate(newpostcontext));
//		$el.find('h2').remove();
//		$el.find('.page-header').prepend(this.template(context));
//             
//                  app.Posts.each(this.addOne, this);
//                 
//             
//            
//         },
//         addOne:function(modelpost){
//         
//            if (app.Posts.type==="tags"){
//               console.log('tags');
//               view=new app.views.Tag({model:modelpost});//this need the parse specification of json
//               $("#taglist").append(view.render().el);
//               this.views.push(view);
//            }
//            else if (app.Posts.type==="categories"){
//               console.log('cats');                          
//               view=new app.views.Category({model:modelpost});//this need the parse specification of json
//               $("#categorylist").append(view.render().el);
//               this.views.push(view);
//            }
//            else  if (this.options.category==="about"){
//                view=new app.views.About({model:modelpost});
//               $("#posts").append(view.render().el);
//             
//            }
//            else{
//               view =new app.views.Post({model:modelpost});
//               this.views.push(view);
//               $("#posts").append(view.render().el);
//             }
//          
//	    
//	 },
//         doNothing:function(e){
//        //     console.log('nothing');
//             if ( e.keyCode === ENTER_KEY )
//               return false
//            return 
//         },
//        
//         createNewPost:function(e){
//             
//          if (e.keyCode === ENTER_KEY || e.type === "click") {
//               
//            
//         //if (app.Posts.length==1){
//          //       app.Posts.url='/posts/'+ this.options.category;
//          //       window.siterouting.navigate('!/'+ this.options.category);
//                // window.App=new AppView({"category":this.options.category});
//            //}  
//            
//               
//               //_.each(this.views,function(view){
//               //       console.log($(view.el));
//               //        view.model.unbind("change", view .render);
//               //       view.undelegateEvents();});//clear all views
//           
//               this.body = $(this.el).find("#new-post-body");
//               this.title=$(this.el).find("#new-post-title");
//               this.summary = $(this.el).find("#new-post-summary");
//               this.tags=$(this.el).find("#new-post-tags");
//               this.category=$(this.el).find("#new-post-category");
//
//          
//            app.Posts.create({title:this.title.val(),summary:this.summary.val(),
//                             body:this.body.val(),category:this.category.val(),
//                             tags:this.tags.val().split(',')});//add event
//      
//            //clear them after submission
//            this.$("#new-post-body").val('');
//            this.$('#new-post-tags').val('');
//            this.$("#new-post-title").val('');
//            this.$("#new-post-category").val('');
//            this.$("#new-post-summary").val('');
//            this.unbind();
//      
//
//           
//            return false;
//         }
//            
//         }
//
//     
//        
//    });
//    
//    
//   
//
//    
//    
//     var runonce=true
//    //  disqview();
//    // $('#disqus_thread').hide();
//     window.siterouting=new  app.routes.Main;
//     Backbone.history.start({pushState: true});
//
//    $("#editabout a").on("click",function(){
//       var  url=location.pathname.substring(1);
//        window.App=new app.views.Main({"url":url});
//      });
//  
//  
//   
//   
//  });
//});

_.extend(App, Backbone.Events);

window.App = App;




