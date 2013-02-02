(function(model){
    var  converter = new Showdown.converter();
     var ENTER_KEY=13;
    app.views.Post=Backbone.View.extend({
        
	model:model,
        className: "post clear" ,//view is a post
        template :Handlebars.compile($("#entry-template").html()),
        initialize: function(){
	   console.log('model change');
            this.model.on('change', this.render, this);//rerender event, callback, [context]
            this.model.on('destroy', this.remove, this);
	    
           // this.model.on('reset', this.render, this)
            //this.render();
            
     
        },
        
     
    
     
      
       events: {
	//"click div.viewable":              "getAPost",
	//"click  h3.viewable":              "getAPost",
        "click  div.editable.admin":          "editBody",//{"eventType selector": "callback"}.
        "click  h3.editable.admin":         "editTitle",
        "click  .save":          "close",
        "keypress .post textarea"  :   "updateHeight",
        "keypress #post-title "  :    "updateOnEnter",
        "keypress #post_tag"  :    "updateOnEnter",
        "click .destroy" : "clear",
        "click .backlink a" : 'resetCollection',
        "click .edit-tags":"editTags",
	"click .edit-title":"editTitle",

       },
    
       render: function() {
           
	    this.body= converter.makeHtml(this.model.toJSON().body);
        
	    body100=false;
            if (app.Posts.length==1) 
	        editmode=true
	    else {
		//if (this.body.length>150) {
		//        body100=true
		//	this.body=this.body.substring(0,150)+"...";
		//                     
		//}
		
	        editmode=false
	    }
            this.title=this.model.toJSON().title;
            this.id=this.model.toJSON().id;
            this.tags=[]
            this.tags=this.model.toJSON().tags;
	    this.category=this.model.toJSON().category;
            var tagsnames=[];
            console.log(typeof this.tags);
            if (typeof this.tags[0]==="object")
               {
               this.tags.forEach(function(tag){//example of a closure
                 tagsnames.push(tag.tag);               
               });
               this.tagsnames=tagsnames;
	       console.log(tagsnames);
	    //   this.tags=tagsnames;
               }
            else//categories and tags return Array
               {
               var tagsArray=[]
            
               this.tagsnames=this.tags;
               }
        
        
           

	     
	    if ((app.Posts.category) || (app.Posts.tag))//tag or category collection
		{  //app.Posts.url='posts/'+this.id;
                    context = {title: this.title,body:this.body,key:this.id,user_admin:window.App.user.toJSON().user_status.user_status,
                 tags: this.tags,date:this.model.toJSON().date,updated:this.model.toJSON().updated,
                 onepostmode:editmode,catid:this.model.toJSON().catid,category:this.category,  body100:  body100}
                }
                else{
                           
                    context = {title: this.title,body:this.body,key:this.id,user_admin:window.App.user.toJSON().user_status.user_status,
                 tags:this.tags,date:this.model.toJSON().date,updated:this.model.toJSON().updated,
                 onepostmode:editmode,catid:this.model.toJSON().catid,category:this.model.toJSON().category,  body100:  body100}
            
            }
	    
       
            var $el=$(this.el);//for DOM hooking}
        
            $el.html(this.template(context));
            $el.find('.save').addClass('hide');
            
           
            runonce=false;
            
           //if (!editevent){
           //    // console.log('reset');
           //     disqconf={}
           //     disqconf.title=this.title;
           //     disqconf.id=this.id;
           //   //  reset(disqconf);
           //     editevent=false;
           // }
           // 
               (function() {
        var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
        po.src = 'https://apis.google.com/js/plusone.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
      })();
	          $.getScript("http://platform.twitter.com/widgets.js");
	     
            return this;
            
       },
    

        
        resetCollection:function(){
         app.Posts.reset();
        },
        editBody: function() {
            editevent=true;
            $(this.el).removeClass('view');
            $(this.el).find('.save').removeClass('hide');
            $(this.el).find('.article').addClass('hide');
	    height=$(this.el).find('.article').height()+20;
            $body=$(this.el).find('textarea').height(height);
            $body.addClass('edit');
	    console.log(toMarkdown(this.body));
            $body.val(toMarkdown(this.body));
	    
	   
         
           
        },
        editTitle:function(){
              editevent=true;
            $(this.el).removeClass('view');
            $(this.el).find('.save').removeClass('hide');
	    $(this.el).find('h3').addClass('hide');//hide textarea and h3
            $(this.el).find('textarea').addClass('hide');
            $title=$(this.el).find('#post-title');
            $title.addClass('edit');
            $title.val(this.title);
        },
        
          editTags:function(){
            $(this.el).removeClass('view');
            $(this.el).find('.tag').addClass('hide');//hide tag
         
            $tags=$(this.el).find('#post_tag');
            $tags.addClass('edit');
            $tags.val(this.tagsnames);
        },
        
        close: function() {
		var tags=[];
                $.getScript("http://platform.twitter.com/widgets.js");
                if ($(this.el).find('h3').hasClass('hide')) {//closing title field
                   title=$(this.el).find('#post-title').val();
		   }
                else{
			//console.log($(this.el).find('.title').text());
                   title=$(this.el).find('.title').text().replace(/!^\s+|\s+|!\s+$/g, " ");
		}
                if ($(this.el).find('.article').hasClass('hide')){
                    bodyMarkup=$(this.el).find('textarea').val();
		  //  this.tags=tags=$(this.el).find('.tag').text().split(',');
                  
                    $(this.el).find("textarea").removeClass('edit');
                    $(this.el).find(".article").removeClass('hide');         
                }
                else
                    bodyMarkup=$(this.el).find('.article').text();
		
                if ($(this.el).find('.tag').hasClass('hide')){
                    tags=$(this.el).find('#post_tag').val().split(',');
                     console.log(tags);
                  }
                else if ((!$(this.el).find('.links').has('a').length) && ($(this.el).find('#post_tag').hasClass('edit'))){//first tag
                     tags=$(this.el).find('#post_tag').val().split(',');
		}
                else{
			 tags=this.tagsnames;
		     
		}
		     // console.log(!$(this.el).find('.links').has('a').length);
               //console.log($(this.el).find('#post_tag').hasClass('edit'));
		console.log(bodyMarkup);
                id=$(this.el).children().attr("id");
            
                if (!id){
                    id=$(".post").filter(function(index) {
                        return (app.Posts.length-1);}).children().attr("id");
                   
                    id=parseInt(id)+1}
                

                
                this.model.save({body: bodyMarkup,title:title,id:id,tags:tags});//a change event is fired
                //this.remove();//this removes the view from the DOM
                this.unbind();//removing all view events 
         
		},
        
        
        updateHeight:function(){
            height=$(this.el).find('.article').height()+20;
            $(this.el).find('textarea').height(height);
	    this.model.body=$(this.el).find('textarea').val();
	    var count=$(this.el).find('textarea').val().length;
	   return
                
         
        },
        updateOnEnter:function(e){
	 
            if ( e.keyCode === ENTER_KEY ){
		    this.close();
			}
           return
           
            
            
            
        },
        clear: function() {
//		if (app.Posts.length===1){
                // app.Posts.url="posts/"+this.id;
             //    window.App=new AppView();//{"category":app.Posts.category}
//                }
                this.model.destroy();//remove event is fired
                this.unbind();
	}
        
        
    });
})(app.views);