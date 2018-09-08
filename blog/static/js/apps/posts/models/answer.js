'use strict';


var Backbone = require('backbone');


var Answer =  Backbone.Model.extend({
  p_answer: "",
  is_correct: false,
  nof_selections: 0


});

module.exports = Answer;


