(function(){
    app.collections.Tags=Backbone.Collection.extend({
        model:app.models.Post,
     
	initialize:function(models,options){
            if (options['url']) {
		   

                   
		    this.url='posts/'+options['url'];
          
                }
	},
	
	    parse:function(data){
		this.type=data.type;
		this.dataheader= data.header;
		console.log(this.header);
		return data.tags;
	    },
        
        
        
    });
})(app.collections);