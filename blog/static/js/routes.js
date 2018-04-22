'user strict';


App.Routers = App.Routers || {}; //initialize

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

		var app = App.startSubApplication(PostsApp);

		app.showPostEditor(postId);
	}


	getAnswers(category, month, year, title) {

	    App.mainRegion = new Region({el: '#answers-container'});
	    var app = App.startSubApplication(PostsApp);


		app.showAnswers(category, month, year, title);
	}
	
  startApp(){

    var app = App.startSubApplication(PostsApp);
		app.showPostsList();

  }
	
	
}

App.Routers.PostsRouter = PostsRouter;
