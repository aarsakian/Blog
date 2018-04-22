'use strict';

App.Collections = App.Collections || {};

class AnswersCollection extends Backbone.Collection{
	constructor(options) {
		super(options);
		this.url = '/api/answers/'+options.title;
	}
	
	
}

