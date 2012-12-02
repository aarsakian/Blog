(function(model){
    app.views.Tag=Backbone.View.extend({
      model:model,
      tagName: "li" ,//append li is a post
      template :Handlebars.compile($("#tags-template").html()),
      initialize: function(){
            console.log("TagVIew");
           // this.model.on('change', this.render, this);//rerender event, callback, [context]
         //   this.model.on('destroy', this.remove, this);
           
         
      },
      
      render:function(){
       
         this.tag=this.model.toJSON().tag;
         this.id=this.model.toJSON().id;
      
         context={tag:this.tag,id:this.id}
         console.log(this.tag)
         $(this.el).html(this.template(context));
  
         return this
      }
      });
})(app.views);