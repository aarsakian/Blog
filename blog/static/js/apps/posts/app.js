'use strict';

class PostsApp {
   constructor(options){
    this.region = options.region;
   }

   showPostsList() {
      App.trigger('loading:start');
      App.trigger('app:posts:started');
      new PostCollection().fetch({
         success: (collection) => {
       
            this.showPosts(collection);
            App.trigger('loading:stop');
         },
         
         fail: (collection, response) => {
            // Show error message if something goes wrong
            App.trigger('loading:stop');
            App.trigger('server:error', response);
         }
    });
   }
   
   showPosts(posts) {
      var postList = this.startController(PostList);

      postList.showList(posts);
   }
   
   showPostEditor(postId) {
      App.trigger('loading:start');
      App.trigger('app:contacts:started');
      
      new Post({id: postId}).fetch({
         success: (model) => {     
            this.showEditor(model);
            App.trigger('loading:stop');
      },
      fail: (collection, response) => {
         console.log(postID);
        App.trigger('loading:stop');
        App.trigger('server:error', response);
      }
    });
  }
  
   showEditor(post) { 
      var postEditor = this.startController(PostEditor);
      postEditor.showEditor(post);
   }

   
   startController(Controller) {
    if (this.currentController &&
        this.currentController instanceof Controller) {
      return this.currentController;
    }

    if (this.currentController && this.currentController.destroy) {
      this.currentController.destroy();
    }

    this.currentController = new Controller({region: this.region});
    return this.currentController;
  }

}