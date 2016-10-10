(function(){
    app.collections.Categories=app.collections.Tags.extend({
		parse:function(data){
		this.type=data.type;
		this.dataheader= data.header;
		console.log(this.header);
		return data.categories;
		}
	    });			   
    
})(app.collections);
