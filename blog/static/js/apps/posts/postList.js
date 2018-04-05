'use strict';

class PostListLayout extends Layout {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#post-list-layout';
    this.regions = {
      actions: '.actions-bar-container',
      list: '.list-container',
      postform: '.post-form-container'
    };
  }

}

class TagListLayout extends Layout {
  constructor(options) {
    super(options);
    this.template = '#tag-list-layout';
    this.regions = {
      list: '.tag-list-container',
    };
  }
}


class TagListView extends CollectionView {
  constructor(options) {
    super(options);
    this.modelView = TagListItemView;
  }

  get className() {
    return 'tag-list';
  }
  
  get events() {

    return {
    }
  }
  
}

class TagListItemView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#tag-list-item';
  }

  get className() {
    return 'tag'; // for each item asssign class
  }

  get events() {
    return {
      'click .destroy': 'deletePost',
      'click #view': 'viewPost',
      'click .edit': 'editPost'
    };
  }

  initialize(options) {
    this.listenTo(options.model, 'change', this.render);
  }

  deletePost() {
    this.trigger('delete', this.model);
  }

  viewPost() {
    var tagId = this.model.get('id');
    App.router.navigate(`edit/tag/${tagId}`, true);
  }
  
  editTitle() {
     this.trigger('edit:title', this.model);  
  }
  
  editPost() {
    this.trigger('edit', this.model);  
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


class PostListView extends CollectionView {
  constructor(options) {
    super(options);
    this.modelView = PostListItemView;
  }

  get className() {
    return 'post-list';
  }
  
  get events() {

    return {
    }
  }
  
}


class PostListItemView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-list-item';
  }

  get className() {
    return 'post'; // for each item asssign class
  }

  get events() {
    return {
      'click .destroy': 'deletePost',
      'click #view': 'viewPost',
      'click .edit': 'editPost'
    };
  }

  initialize(options) {
    this.listenTo(options.model, 'change', this.render);
           
  //  var tagList = new TagListView({collection: options.model.tags});
 
  }

  deletePost() {
    this.trigger('delete', this.model);
  }

  viewPost() {
    var postId = this.model.get('id');
    App.router.navigate(`edit/${postId}`, true);
  }
  
  editTitle() {
     this.trigger('edit:title', this.model);  
  }
  
  editPost() {
    this.trigger('edit', this.model);  
  }

}



class PostList {
  constructor(options) {
    // Region where the application will be placed
    this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);
  }

  showList(posts) {
    // Create the views
    var layout = new PostListLayout();
    
    //var actionBar = new PostListActionBar();
 
    
    var titleForm = new TitleForm();

    var postForm = new PostForm({model: new Post(),
                                collection:posts});
  
    // Show the views
    this.region.show(layout);
    
 
  //  layout.getRegion('actions').show(actionBar);
    var postList = new PostListView({collection:
                                    posts});
    
    layout.getRegion('list').show(postList);
    layout.getRegion('postform').show(postForm);
    
    
    this.listenTo(postList, 'item:delete', this.deletePost);
    this.listenTo(postList, 'item:edit:title', this.editTitlePost);
    this.listenTo(postList, 'item:edit', this.editPost);
    this.listenTo(postForm, 'form:save', this.savePost);
    this.listenTo(postForm, 'form:cancel', this.cancel);
    
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




class PostForm extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-form';

  }

  get className() {
    return 'form-horizontal';
  }

  get events() {
    return {
      'click #submit': 'savePost',
      'click #cancel': 'cancel'
    };
  }

  serializeData() {
    return _.defaults(this.model.toJSON());
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

    var answers = [];
    answers.push( _.map(answers_a, function (answer, idx){
        return {'p_answer': answer, 'is_correct':areCorrect[idx]}
    }));

    var collection = this.collection;
    var posts = {};
    this.model.set('answers', answers);

    this.model.save(null, {
      success(model, response, options) {
        // Redirect user to contact list after save
     //   App.notifySuccess('Post saved');
        collection.trigger('add', model);
        
      },
      error() {
        // Show error message if something goes wrong
     //   App.notifyError('Something goes wrong');
      }
    });

    this.trigger('form:save', this.model);
    this.clearForm();
    //clear the model
    this.model = new Post();
  }
  
  clearForm() {
    this.clearInput("#new-post-body");
    this.clearInput('#new-post-tags');
    this.clearInput("#new-post-title");
    this.clearInput("#new-post-category");
    this.clearInput("#new-post-summary");
    this.clearInputs(".new-post-answer");
  }
  getInput(selector) {
    return this.$el.find(selector).val();
  }
  getInputs(selector) {
    var vals = [];
    this.$el.find(selector).each(function(index) {
        vals.push($(this).val())
    });
    return vals;
  }

  getInputsCheckbox(selector) {
    var vals = [];
    this.$el.find(selector).each(function(index) {
        vals.push($(this).is(':checked'));
    });
    return vals;
  }

  clearInput(selector) {
    this.$el.find(selector).val('');
  }

  clearInputs(selector) {
     this.$el.find(selector).each(function(index) {
       $(this).val('');
    });
  }

  cancel() {
    this.trigger('form:cancel');
  }
}

class TitleForm extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-title-input-field';
  }
  
  get events() {
    return {
      'click #submit': 'saveTitle',
      'click #cancel': 'cancel'
    };
  }
}