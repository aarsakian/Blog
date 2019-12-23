'use strict';

var Backbone = require('backbone');
var $ = require('jquery');
var _ = require('underscore');


class Tag extends Backbone.NestedModel {
  constructor(options) {
    super(options);
    this.urlRoot = '/api/tags';
  }
  get defaults() {
      return {
        val: "",
        key: ""

      };
  }

  updateTags(options) {
      var ajaxOptions = {
      url: '/api/tags/'+this.get('val'),
      type: 'PUT',
      cache: false,
      contentType: false,
      processData: false
    };
    _.extend(ajaxOptions, _.pick(options, 'success', 'error'));

    $.ajax(ajaxOptions);
  }



}

module.exports = Tag;