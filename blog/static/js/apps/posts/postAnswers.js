'use strict';


class AnswersFormLayout extends Layout {
  constructor(options) {
    super();

    this.regions = {
      postform: '.answers-container'
    };
  }

  get className() {

  }

  initialize(options) {
     this.render();
  }


  get postId() {
  console.log("GETING"+this.$el.data('id'));
     return this.$el.data('id');
  }
}


class AnswersForm extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-answers';
  }

  get events() {
    return {
      'click #submit': 'submitAnswers',

    };
  }
}


class Answers {
  constructor(options) {
    this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);


  }

  getPostId() {
    var answers = new AnswersFormLayout();
    console.log("SNAS"+Object.keys(answers)+" "+answers.regions[0]);

     this.region.show(answers);
    return answers.postId;
  }

  showAnswers(model) {
     console.log("MODEL"+model);
  }

}


