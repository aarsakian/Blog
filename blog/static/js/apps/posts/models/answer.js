'use strict';

App.Models = App.Models || {};

var Answer =  Backbone.Model.extend({
  p_answer: "",
  is_correct: false,

});


App.Models.Answer = Answer;
