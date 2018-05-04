'use strict';

var Backbone = require('backbone');


class AnswersCollection extends Backbone.Collection{
	constructor(options) {
		super(options);
		this.url = '/api/answers/'+options.title;
	}
	
	
}

module.exports = AnswersCollection;