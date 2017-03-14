'use strict';

class ContactFormLayout extends Layout {
  constructor(options) {
    super(options);
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
    var collection = this.collection;
    var posts = {};
    this.model.save(null, {
      success(model, response, options) {
        // Redirect user to contact list after save
     //   App.notifySuccess('Post saved');
     
       
      },
      error() {
        // Show error message if something goes wrong
     //   App.notifyError('Something goes wrong');
      }
    });

    this.trigger('form:save', this.model);
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

  showEditor(contact) {
    // Create the views
    var layout = new ContactFormLayout({model: contact});

    var postForm = new EditPostForm({model: contact});
 //   var contactPreview = new PostPreview({model: contact});

    // Render the views
    this.region.show(layout);
    layout.getRegion('postform').show(postForm);
  //  layout.getRegion('preview').show(contactPreview);

    this.listenTo(postForm, 'form:save', this.savePost);
    this.listenTo(postForm, 'form:cancel', this.cancel);
  }

  savePost(post) {
    post.save(null, {
      success() {
        // Redirect user to contact list after save
       // App.notifySuccess('Contact saved');
          App.router.navigate(`edit`, true);
      },
      error() {
        // Show error message if something goes wrong
    //    App.notifyError('Something goes wrong');
      }
    });
  }

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
