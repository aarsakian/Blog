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

    var postForm = new PostForm({model: contact});
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
        App.router.navigate(`edit/${post.id}`, true);
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
