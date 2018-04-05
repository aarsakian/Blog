'use strict';

App.Models = App.Models || {};

var Answer =  Backbone.Model.extend({
  p_answer: "",
  is_correct: false
});

class Post extends Backbone.NestedModel {
  constructor(options) {
    super(options);
    this.urlRoot = '/api/posts';
  }

  get defaults() {
    return {
      title:"",
      body:"body of post",
      date:"date of the post",
      updated:"",
      tags:"",
      summary:"",
      answers:[]

    };
  }
}

App.Models.Post = Post;


//(function (models,collection){
//  app.models.Post=Backbone.Model.extend({
//        defaults:{
//            title:"",
//            body:"body of post",
//            date:"date of the post",
//            updated:"",
//            tags:"",
//            summary:""
//
//        },
//
//        initialize: function() {
//
//			if (!this.get("title")) {
//				this.set({"title": this.defaults.title});
//			}
//		},
//        url:function(){
//                    console.log(this.id);
//            if ((this.id=="") || (typeof this.id=="undefined")) {
//
//                return app.Posts.url;
//            }
//            else {//collection ==a model
//           //    if (app.Posts.length==1)
//             //       return app.Posts.url
//                if (app.Posts.url.split('/').length===3)
//                    return  app.Posts.url;
//		else
//		    return  app.Posts.url+"/"+this.id;
//
//            }
//
//        }
//
//    });
//
//})(app.models);