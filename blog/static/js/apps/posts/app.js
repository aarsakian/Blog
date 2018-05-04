'use strict';

var App = require('../../app');
var PostList = require('./postList');
var PostCollection = require('./collections/postscollection')
var AnswersCollection = require('./collections/answerscollection')
var Post = require('./models/post');

var Answers = require('./postAnswers');


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

   showAnswers(category, month, year, title) {


      App.trigger('loading:start');
      App.trigger('app:posts:started');
      new AnswersCollection({"title":title}).fetch({
         success: (collection) => {
            var answersController = this.startController(Answers);
            answersController.showAnswers(collection);
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

        App.trigger('loading:stop');
        App.trigger('server:error', response);
      }
    });
  }
  
   showEditor(post) {
      var PostEditor = require('./postEditor');
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

module.exports = PostsApp;