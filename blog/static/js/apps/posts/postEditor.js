'use strict';


var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;
var PostForm = require('./postList').PostForm;


class ContactFormLayout extends Layout {
  constructor(options) {
    super({tagName:"div",className:"col"});
    this.template = '#post-form-layout';
    this.regions = {
      preview: '#preview-container',
      postform: '.post-form-container'
    };
  }

  get className() {
    
  }
}


class PostPreview extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-form-preview';
  }
}



class EditPostForm extends PostForm {
  constructor(options) {
    super(options);
    

  }

  
  savePost(event) {
    event.preventDefault();
    this.model.set('body',this.getInput('#new-post-body'));
    this.model.set('title',this.getInput('#new-post-title'));
    this.model.set('summary',this.getInput('#new-post-summary'));
    this.model.set('tags',this.getInput('#new-post-tags').split(','));
    this.model.set('category',this.getInput('#new-post-category'));

    var answers_a = this.getInputs('.new-post-answer');
    var areCorrect = this.getInputsCheckbox('.form-check-input');//.new-post-answer-is-correct

    var answers = _.map(answers_a, function (answer, idx){
        return {'p_answer': answer, 'is_correct':areCorrect[idx]}
    });

    var collection = this.collection;
    var posts = {};
    this.model.set('answers', answers);

    var csrf_token = this.getInput('#csrf_token');
    this.model.save(null, {
      beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        },
      success(model, response, options) {
        // Redirect user to contact list after save
     //   App.notifySuccess('Post saved');

         App.router.navigate('edit', true);
       
      },
      error() {
        // Show error message if something goes wrong
     //   App.notifyError('Something goes wrong');
      }
    });


  //  this.trigger('form:save', this.model);
//    this.clearForm();
  }
  
 
}

class PostEditor {
  constructor(options) {
    this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);
  }

  showEditor(post) {
    // Create the views

    var layout = new ContactFormLayout({model: post});

    var postForm = new EditPostForm({model: post});

    // Render the views
    layout.$el.addClass("row col-12");
    this.region.show(layout);
    layout.getRegion('postform').show(postForm);
  //  layout.getRegion('preview').show(contactPreview);

    this.listenTo(postForm, 'form:save', this.savePost);
    this.listenTo(postForm, 'form:cancel', this.cancel);
  }

 /*savePost(postForm) {

    postForm.save(null, {

      success() {
        // Redirect user to contact list after save
       // App.notifySuccess('Contact saved');


         App.router.navigate('edit', true);
      },
      error() {
        // Show error message if something goes wrong
    //    App.notifyError('Something goes wrong');
      }
    });
  }*/

  cancel() {
    // Warn user before make redirection to prevent accidental
    // cencel
    App.askConfirmation('Changes will be lost', isConfirm => {
      if (isConfirm) {
        App.router.navigate('contacts', true);
      }
    });
  }

  // Close any active view and remove event listeners
  // to prevent zombie functions
  destroy() {
    this.region.remove();
    this.stopListening();
  }
}

module.exports = PostEditor;