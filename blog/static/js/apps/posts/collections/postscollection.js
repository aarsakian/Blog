'use strict';

var Backbone = require('backbone');

class PostCollection extends Backbone.Collection{
	constructor(options) {
		super(options);
		this.url = '/api/posts';
	}
	
	
}


module.exports = PostCollection;