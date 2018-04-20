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
