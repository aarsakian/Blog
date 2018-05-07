'user strict';

var Backbone = require('backbone');

var Region = require('./common').Region;

class PostsRouter extends Backbone.Router {
  constructor(options) {
	super(options);
	this.routes = {
      'edit': 'displayPosts',
	  'tags': 'displayPosts',
	  'edit/:key': 'editPost',
	  ':category/:month/:year/:title' : 'getAnswers'
	};
    this._bindRoutes();
  }
  
	editPost(postId) {
         var region  = new Region({el: '#bd'});
	    var app = this.startApp(region);
		app.showPostEditor(postId);
	}


	getAnswers(category, month, year, title) {


	    var region = new Region({el: '#answers-container'});
        var app = this.startApp(region);
	    app.showAnswers(category, month, year, title);
	}

	displayPosts() {
	    var region  = new Region({el: '#bd'});
	    var app = this.startApp(region);

	    app.showPostsList();

	}

  startApp(region){

     var App = require('./app');
     var PostsApp = require('./apps/posts/app');

     var app = App.startSubApplication(PostsApp, region);


     return app

  }
	
	
}

module.exports = new PostsRouter();
