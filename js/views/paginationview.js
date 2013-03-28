(function(view){
    view.Pagination=Backbone.View.extend({
      
       tagName:'aside'   ,//element here$("#pagination-area")
      template :Handlebars.compile($("#pagination-template").html()),
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