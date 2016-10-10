(function(){
      var  converter = new Showdown.converter();
    app.views.About=app.views.Post.extend({
       
        className: "post clear" ,//view is a post
        template :Handlebars.compile($("#about-template").html()),
        initialize: function(){
         console.log("ABOUT");
           //PostView.initialize();
             this.model.on('change', this.render, this);//rere
         
        },
       
     
          events: {
     
               "click .save":  "save",
               "dblclick div.editable.admin":"editBody"
          
         },
         
      save: function (){
          app.views.Post.prototype.close.call(this);
          $(this.el).find("textarea").removeClass('edit');
          $(this.el).find(".aboutpost").removeClass('hide');
         
      },
      
       editBody: function (){
         console.log('editbody');
          app.views.Post.prototype.editBody.call(this);
         
      },
         
         
       render: function() {
          //  console.log(AboutView.prototype);
            this.body= converter.makeHtml(this.model.toJSON().body);
            //this.body=toMarkdown(this.body);
           //console.log(this.body);
	    this.tags=this.model.toJSON().tags;
            this.id=this.model.toJSON().id;
            this.updated=this.model.toJSON().updated;
            this.tagsnames=[]
               console.log(this.tags);
            if (typeof this.id!="undefined"){
               if (app.collections.Posts.length==1)
               app.collections.Posts.url="posts/"+this.model.toJSON().category+"/"+this.id;
          
             }
            this.title=this.model.toJSON().title;
           
        
            context = {title: this.title,body:this.body,key:this.id,user_admin:window.App.user.toJSON().user_status.user_admin,
            "updated":this.updated}
           
            var $el=$(this.el);//for DOM hooking}
        
            $el.html(this.template(context));

            runonce=false;
            
          
            return this;
            
       }
      
      
      });
})(app.views.Post);