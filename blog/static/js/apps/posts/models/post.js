'use strict';



var Backbone = require('../../../libs/backbone/backbone-nested');

class Post extends Backbone.NestedModel {
  constructor(options) {
    super(options);
    this.urlRoot = '/api/posts';

   this.validation = {
      title: {
        required: true,
        minLength: 15
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
      answers:[]

    };
  }


}

module.exports = Post;
