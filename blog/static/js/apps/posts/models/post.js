'use strict';


var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('../../../libs/backbone/backbone-nested');


class Post extends Backbone.NestedModel {
  constructor(options) {
    super(options);
    this.urlRoot = '/api/posts';

   this.validation = {
      title: {
        required: true,
        minLength: 5,
      },
      category: {
        required: true,
        minLength: 2
      }
    };

  }

  get defaults() {
    return {
      title:"",
      body:"body of post",
      date:"date of the post",
      category:"",
      updated:"",
      tags:"",
      summary:"",
      images:[],
      answers:[]

    };
  }

  uploadImage(imageBlob, options) {
    // Create a form object to emulate a multipart/form-data
    var formData = new FormData();
    formData.append('image', imageBlob);



    var ajaxOptions = {
      url: '/api/posts/' + this.get('id') + '/images',
      type: 'POST',
      data: formData,
      cache: false,
      contentType: false,
      processData: false
    };

    options = options || {};

    // Copy options to ajaxOptions
    _.extend(ajaxOptions, _.pick(options, 'success', 'error'));

    // Attach a progress handler only if is defined
    if (options.progress) {
      ajaxOptions.xhr = function() {
        var xhr = $.ajaxSettings.xhr();

        if (xhr.upload) {
          // For handling the progress of the upload
          xhr.upload.addEventListener('progress', event => {
            let length = event.total;
            let uploaded = event.loaded;
            let percent = uploaded / length;

            options.progress(length, uploaded, percent);
          }, false);
        }

        return xhr;
      };
    }

    $.ajax(ajaxOptions);
  }


}

module.exports = Post;
