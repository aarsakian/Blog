(function(model){ 
    app.views.Category=Backbone.View.extend({
      model:model,
      tagName: "li" ,//append li is a post
      template :Handlebars.compile($("#categories-template").html()),
      initialize: function(){
           console.log("catVIew");
           // this.model.on('change', this.render, this);//rerender event, callback, [context]
         //   this.model.on('destroy', this.remove, this);
           
         
      },
      
      render:function(){
       
         this.category=this.model.toJSON().category;
         this.catid=this.model.toJSON().catid;
      
         context={category:this.category,id:this.catid}
         $(this.el).html(this.template(context));
  
         return this
      }
      });
})(app.views);