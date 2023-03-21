'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');

class Image extends Backbone.NestedModel {
    constructor(options) {
      super(options);
      this.urlRoot = '/api/images';
  
    }

    get defaults() {
        return {
            filename: null
    
        };
      
    }

    publish(options) {
        var ajaxOptions = {
          url: this.urlRoot + '/' + this.get('filename') + '/publish',
          type: 'GET',
          cache: false,
          contentType: false,
          processData: false
        };
        _.extend(ajaxOptions, _.pick(options, 'success', 'error'));
    
        $.ajax(ajaxOptions);
      }


      unpublish(options) {
        var ajaxOptions = {
          url: this.urlRoot + '/' + this.get('filename') + '/unpublish',
          type: 'GET',
          cache: false,
          contentType: false,
          processData: false
        };
        _.extend(ajaxOptions, _.pick(options, 'success', 'error'));
    
        $.ajax(ajaxOptions);
      }
}

module.exports = Image;