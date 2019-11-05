'use strict';

var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;
var CollectionView = require('../../common').CollectionView;
var BackboneValidation = require('../../common').BackboneValidation;
var Post = require('./models/post');
var Marked = require('marked');
var Renderer = require('marked-forms')(new Marked.Renderer());




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
      'click .edit': 'editPost',
      'click .edit-tags': 'editTags',
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

  editTags() {
    this.trigger('edit:tags', this.model);
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

    var postForm = new PostForm({model: new Post()});
  
    // Show the views

    this.region.show(layout);


  //  layout.getRegion('actions').show(actionBar);

    var postList = new PostListView({collection:
                                    posts});

    layout.getRegion('list').show(postList);
    layout.getRegion('postform').show(postForm);

    this.posts = posts;
    
//Tell an object to listen to a particular event on an other object. b
    this.listenTo(postList, 'item:delete', this.deletePost);
    this.listenTo(postList, 'item:edit:title', this.editTitlePost);
    this.listenTo(postList, 'item:edit:tags', this.editTags);
    this.listenTo(postList, 'item:edit', this.editPost);
    this.listenTo(postForm, 'form:save', this.savePost);
    this.listenTo(postForm, 'form:cancel', this.cancel);
    
  }
  
  savePost(post) {
    this.posts.trigger('add', post);

  }
  
  editTitlePost(view, post) {
    var title = post.get('title');
    
  }

  editTags(view, post) {

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
      'click #post-submit': 'savePost',
      'click #cancel': 'cancel',
      'keydown #new-post-body': 'previewMarkdownAndResizeTextArea',
      'change #files': 'fileSelected'
    };
  }

  fileSelected(event) {
    event.preventDefault();

    // Get a blob instance of the file selected
    var $fileInput = this.$('#files')[0];
    var fileBlob = $fileInput.files[0];

    // Render the image selected in the img tag
    var fileReader = new FileReader();
    fileReader.onload = event => {

      if (this.model.isNew()) {
        this.model.set({
          image: {
            url: event.target.result,
            filename: this.$('#files').val()
          }
        });
      }
    };
    fileReader.readAsDataURL(fileBlob);

    this.trigger('image:selected', fileBlob);
  }


  serializeData() {
    var str = JSON.stringify(this.model.toJSON());

    return _.defaults(this.model.toJSON());
  }

  onRender() {

   BackboneValidation.bind(this);
  }

  savePost(event) {
    event.preventDefault();



    this.model.set('body',this.getInput('#new-post-body'));
    this.model.set('title',this.getInput('#new-post-title'));
    this.model.set('summary',this.getInput('#new-post-summary'));
    this.model.set('tags',this.getInput('#new-post-tags').split(','));
    this.model.set('category',this.getInput('#new-post-category'));

    if (!this.model.isValid(true)) {
      return;
    }

    var answers_a = this.getInputs('.new-post-answer');
    var areCorrect = this.getInputsCheckbox('.form-check-input');//.new-post-answer-is-correct

    var answers = _.map(answers_a, function (answer, idx){
        return {'p_answer': answer, 'is_correct':areCorrect[idx]}
    });


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

  previewMarkdownAndResizeTextArea(e) {
      this.previewMarkdown();
      this.resizeTextArea();
  }

  previewMarkdown() {
      var markdownText = this.getInput('#new-post-body');

      var html = Marked(markdownText, {renderer:Renderer});
      $('#preview-post-body').html(html);

  }
  resizeTextArea() {
     $("#new-post-body").keyup(function(e) {
        while($(this).outerHeight() <
          this.scrollHeight + parseFloat($(this).css("borderTopWidth")) +
           parseFloat($(this).css("borderBottomWidth"))) {
            $(this).height($(this).height()+1);
        };
     });
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



module.exports = {PostForm, PostList};
