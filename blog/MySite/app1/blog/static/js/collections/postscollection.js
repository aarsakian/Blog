(function(collection,model){ 
    collection.Posts=Backbone.Collection.extend({
        model:model,

        initialize:function(models,options){
	  console.log(options);
            if (typeof options!="undefined"){
                 
                if (options['category']){
		    
                    this.category=options['category'].replace('!','');
                    this.url='categories/'+this.category;
		    console.log(this.url);
		    this.header=this.category;
                }
              
             
                else if (options['tag'])
                {   
		    this.tag=options['tag'].replace('!','');
                    this.url='tags/'+this.tag;
		    this.header=this.tag
                 
                }
		else if (options['about'])
                {   
		    this.about=options['about']
                    this.url='posts/about';
		    this.header="About";
                 
                }

		
		else if (options['postkey'])
		{    
		    // this.header=options['postTitle'];
		    console.log(this.url);
		     this.url='/posts/'+options['postkey'];
		    
		}
              
            }
	    else
                this.url='posts'//home url
           
        },
	
        parse:function(data){
	    this.type=data.type;   
	    this.dataheader=data.header;
            return data.posts;
        }
        
        
        
    });
})(app.collections,app.models.Post);
    
