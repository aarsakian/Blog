'user strict';


App.Routers = App.Routers || {}; //initialize

class PostsRouter extends Backbone.Router {
  constructor(options) {
	super(options);
	this.routes = {
    'edit': 'startApp',
	  'tags': 'displayPosts',
	  'edit/:key': 'editPost'
	};
    this._bindRoutes();
  }
  
	editPost(postId) {

		var app = App.startSubApplication(PostsApp);

		app.showPostEditor(postId);
	}
	
  startApp(){

    var app = App.startSubApplication(PostsApp);
		app.showPostsList();

  }
	
	
}

App.Routers.PostsRouter = PostsRouter;
