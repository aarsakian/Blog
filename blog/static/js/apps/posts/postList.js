'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;
var CollectionView = require('../../common').CollectionView;
var BackboneValidation = require('../../common').BackboneValidation;
var Post = require('./models/post');
var Tag = require('./models/tag');
var marked = require('marked');
var markedForms = require('marked-forms');



class PostListLayout extends Layout {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#post-list-layout';
    this.regions = {
      actions: '.actions-bar-container',
      list: '.list-container',
      tagsform: '.tag-list-container',
      postform: '.post-form-container',
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
      'click .destroy': 'deleteTag',
      'click .edit': 'editTag'

    };
  }

  initialize(options) {
    this.listenTo(options.model, 'change', this.render);
    this.listenTo(options.model, 'change', options.model.updateTags);
  }

  onRender() {

   BackboneValidation.bind(this);
  }

  deleteTag() {
 
     this.model.destroy({

            success() {
                // App.notifySuccess('Contact was deleted');
            },
            error() {
                //  App.notifyError('Ooops... Something went wrong');
            }
     });
  }

  editTag(event) {
    var new_tag = $(event.currentTarget).prev().val();
    this.model.set("val", new_tag);
    this.model.updateTags({
      success: () => {
        // Tell to others that upload was done successfully
        this.trigger('tag:editing:done', this.model.val);

      },
      error: err => {
        // Tell to others that upload was error
        this.trigger('avatar:deleting:error', err);
      }
    });

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
    this.layout = new PostListLayout();
    
    //var actionBar = new PostListActionBar();
 
    
    var titleForm = new TitleForm();

    var postForm = new PostForm({model: new Post()});
  
    // Show the views

    this.region.show(this.layout);


  //  layout.getRegion('actions').show(actionBar);

    var postList = new PostListView({collection:
                                    posts});

    this.layout.getRegion('list').show(postList);
    this.layout.getRegion('postform').show(postForm);

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
        var tags = new Backbone.Collection(null, {
            model: Tag
        });
        post.get("tags").forEach(tag=>
          {tags.push(new Tag({val:tag["val"], key:tag["key"]}))});
      
        var tagList = new TagListView({collection:tags});

        this.layout.getRegion('tagsform').show(tagList);

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
      'change #files': 'fileSelected',
      'click .delete-image': 'deleteImage'
    };
  }

  fileSelected(event) {
    event.preventDefault();

    // Get a blob instance of the file selected
    var $fileInput = this.$('#files')[0];
    var $preview = this.$('#preview')
    var files = $fileInput.files;
    var postform = this;
    // Render the image selected in the img tag
    var images = [];
    _.each(files, function(fileBlob){
         var fileReader = new FileReader();
        fileReader.onload = event => {
      if (postform.model.isNew()) {

         images.push({
            url: event.target.result,
            filename: fileBlob.name
          });
        }
        var image = new Image();
        image.height = 150;
        image.title = fileBlob.name;
        image.src = event.target.result;
        preview.appendChild(image);

        postform.model.set('images', images);

    };

    fileReader.readAsDataURL(fileBlob);

    postform.trigger('image:selected', fileBlob);

    });

  }

  deleteImage(event) {
    event.preventDefault();
    this.trigger('image:delete', $(event.currentTarget).data('image-filename'), $(event.currentTarget));
  }


  serializeData() {
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
    this.model.set('category',this.getInput('#new-post-category'));

    let tags = this.getInput('#new-post-tags').split(',')

    if (tags[tags.length-1] === "") {
      tags = tags.slice(0, -1) //remove ""
    }
    this.model.set('tags', tags);
   

    if (!this.model.isValid(true)) {
      return;
    }

    var answers_a = this.getInputs('.new-post-answer');
    var areCorrect = this.getInputsCheckbox('.answers .checkbox input');

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
      marked.use(markedForms)
      var html = marked.marked(markdownText);
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
