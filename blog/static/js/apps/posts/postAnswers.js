'use strict';

var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;


class AnswersLayout extends Layout {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#answers-layout';
    this.regions = {
      answers: '.answers-layout-container',
      gcharts: '.g-charts-layout'
    };
  }

}


class AnswersGraphView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#answers-graph';
    google.charts.load('current', {packages: ['corechart', 'bar']});
  }

   createGraph(response, answersGraphView) {
        google.charts.setOnLoadCallback(answersGraphView.drawBasic(response));

   }

   drawBasic(response) {

      var data = google.visualization.arrayToDataTable(_.pairs(response.answers_stats));

      var options = {
        chartArea: {width: '35%'},
        hAxis: {xx
          title: 'Answers Statistics',
          minValue: 0
        },
        vAxis: {
          title: ''
          textStyle:{
            fontSize:0.5em;
          }
        },
        legend:{position:'none'},
        gridlines: { count: -1}
      };

      var chart = new google.visualization.BarChart(document.getElementById('gviz'));
      chart.draw(data, options);
   }

}




class AnswersView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#post-answers';
    this.answersGraphView = options.answersGraphView;

  }

  get className() {
    return 'post-list';
  }
  
   get events() {
    return {
      'click #submit': 'submitAnswer',
      'click .answer-choice': 'enableSubmitButton'
    };
  }

  submitAnswer(event) {
     event.preventDefault();
     this.clearColors();
     this.findSaveUserAnswer();


  }

  findSaveUserAnswer() {
    var modelView = this;
    this.collection.each(function (model, idx){
          var id = idx+1;
          var checked = modelView.getSelector("#r_answers-"+id).is(':checked');
          if (checked) {
            model.set("is_correct",  'True');
            model.set("idx",  idx);
            modelView.saveModel(model);

           }

    });

  }

  saveModel(model) {
    var csrf_token = this.getInput('#csrf_token');
    var answersView = this;
    model.save(null, {
       beforeSend: function(xhr, settings) {

            xhr.setRequestHeader("X-CSRFToken", csrf_token);

        },
       success(model, response, options) {
        // Redirect user to contact list after save

            if (response.result)  {
               //  App.notifySuccess('You answered correctly');
            }

            answersView.trigger("answer:submitted", response, model.get("idx"), answersView);

            answersView.answersGraphView.trigger("answer:submitted", response, answersView.answersGraphView);

      },
      error() {
        // Show error message if something goes wrong
       //  App.notifyError('Something went wrong');
      }
    });


  }


  enableSubmitButton(event) {
       this.getSelector('#submit').removeClass('disabled');
  }

  getInput(selector) {
     return this.getSelector(selector).val();
  }


  colorAnswer(response, idx, modelView) {
    console.log(" "+".stats-"+idx);
       var colorResult = ""
       if (response.result) {
         colorResult = "bg-success";

       } else {
         colorResult = "bg-danger";
       }
       modelView.getSelector("tr").eq(idx).addClass(colorResult);
       modelView.getSelector("#stats-"+idx).text(response.nof_times_selected);

  }

  getSelector(selector) {
    return this.$el.find(selector);
  }

  clearColors() {

    this.getSelector('tr').removeClass("bg-success").removeClass("bg-danger");
  }


  
}




class Answers {
  constructor(options) {
    // Region where the application will be placed
    this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);
  }

  showAnswers(postAnswers) {
    // Create the views
    var layout = new AnswersLayout();
    //var actionBar = new PostListActionBar();
 
    
    //var titleForm = new TitleForm();


    // Show the views

    this.region.show(layout);
    

  //  layout.getRegion('actions').show(actionBar);
    if (postAnswers.length > 0  ) {

        var answersGraphView = new AnswersGraphView();

        var answersView = new AnswersView({collection:
                                    postAnswers, answersGraphView});

        layout.getRegion('answers').show(answersView);
        layout.getRegion('gcharts').show(answersGraphView);

        this.listenTo(answersView,'answer:submitted', answersView.colorAnswer)
        this.listenTo(answersGraphView,'answer:submitted', answersGraphView.createGraph)

    }


    
  }
  
  addPost(view, post) {
    
    
  }
  
  editTitlePost(view, post) {
    var title = post.get('title');
    
  }
  
  editPost(view, post) {
    App.router.navigate(`edit/${post.id}`, true);
  }
  
  
  deletePost(view, post) {
   // App.askConfirmation('The contact will be deleted', (isConfirm) => {
    //  if (isConfirm) {
        post.destroy({
          success() {
           // App.notifySuccess('Contact was deleted');
          },
          error() {
          //  App.notifyError('Ooops... Something went wrong');
          }
        });
      //}
    //});
  }





  // Close any active view and remove event listeners
  // to prevent zombie functions
  destroy() {
    this.region.remove();
    this.stopListening();
  }
}



module.exports = Answers;