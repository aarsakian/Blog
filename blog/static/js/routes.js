'user strict';

var Backbone = require('backbone');
var PostsApp = require('./apps/posts/app');


class PostsRouter extends Backbone.Router {
  constructor(options) {
	super(options);
	this.routes = {
      'edit': 'startApp',
	  'tags': 'displayPosts',
	  'edit/:key': 'editPost',
	  ':category/:month/:year/:title' : 'getAnswers'
	};
    this._bindRoutes();
  }
  
	editPost(postId) {
        var app = this.startApp();

		app.showPostEditor(postId);
	}


	getAnswers(category, month, year, title) {
        var app = this.startApp();
	    App.mainRegion = new Region({el: '#answers-container'});
	    var app = App.startSubApplication(PostsApp);


		app.showAnswers(category, month, year, title);
	}
	
  startApp(){

     var App = require('./app');
     var PostsApp = require('./apps/posts/app');
     var app = App.startSubApplication(PostsApp);

	 app.showPostsList();


  }
	
	
}

module.exports = new PostsRouter();
