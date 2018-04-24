'use strict';

class AnswersLayout extends Layout {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#answers-layout';
    this.regions = {
      answers: '.answers-layout-container',

    };
  }

}






//class PostListActionBar extends ModelView {
//  constructor(options) {
//    super(options);
//    this.template = '#actions-template';
//  }
//
//  get className() {
//    return 'options-bar col-xs-12';
//  }
//
//  get events() {
//    return {
//      'click button': 'createContact'
//    };
//  }
//
//  createContact() {
//    App.router.navigate('contacts/new', true);
//  }
//}


class AnswersView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-answers';
  }

  get className() {
    return 'post-list';
  }
  
   get events() {
    return {
      'click #submit': 'submitAnswer'
    };
  }

  submitAnswer(event) {
     event.preventDefault();
     console.log("SUBMITTING");
     this.trigger('edit:title', this.model);
  }
  
}





class Answers {
  constructor(options) {
    // Region where the application will be placed
    this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);
  }

  showAnswers(posts) {
    // Create the views
    var layout = new AnswersLayout();
    
    //var actionBar = new PostListActionBar();
 
    
    //var titleForm = new TitleForm();


    // Show the views

    this.region.show(layout);
    
 
  //  layout.getRegion('actions').show(actionBar);
    var answers = new AnswersView({collection:
                                    posts});
    
    layout.getRegion('answers').show(answers);

    
    
   // this.listenTo(postList, 'item:delete', this.deletePost);
    //this.listenTo(postList, 'item:edit:title', this.editTitlePost);
  //  this.listenTo(postList, 'item:edit', this.editPost);
    //this.listenTo(postForm, 'form:save', this.savePost);
    //this.listenTo(postForm, 'form:cancel', this.cancel);
    
  }
  
  addPost(view, post) {
    
    
  }
  
  editTitlePost(view, post) {
    var title = post.get('title');
    
  }
  
  editPost(view, post) {
    App.router.navigate(`edit/${post.id}`, true);
  }
  
  
  deletePost(view, post) {
   // App.askConfirmation('The contact will be deleted', (isConfirm) => {
    //  if (isConfirm) {
        post.destroy({
          success() {
           // App.notifySuccess('Contact was deleted');
          },
          error() {
          //  App.notifyError('Ooops... Something went wrong');
          }
        });
      //}
    //});
  }

  // Close any active view and remove event listeners
  // to prevent zombie functions
  destroy() {
    this.region.remove();
    this.stopListening();
  }
}



