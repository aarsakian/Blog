'use strict';

var _ = require('underscore');
var Backbone = require('backbone');
var Region = require('./common').Region;

require('./routes');


class DefaultRouter extends Backbone.Router {

    constructor(options) {
        super(options);
        this.routes = {
            '/edit': 'defaultRoute'
        };
        this._bindRoutes();
    }

  // Redirect to contacts app by default
  defaultRoute() {

  //  this.navigate('edit', true);
  }

}





var App = {
   Models: {},
   Collections: {},
   Routers: {},

  start() {
    // Initialize all available routes
    _.each(_.values(this.Routers), function(Router) {

      new Router();
    });

    // The common place where sub-applications will be showed


    // Create a global router to enable sub-applications to redirect to
    // other urls

    App.router = new DefaultRouter();

    Backbone.history.start({pushState: true});

  },


     // Only a subapplication can be running at once, destroy any
  // current running subapplication and start the asked one
  startSubApplication(SubApplication, region) {
    // Do not run the same subapplication twice

    if (this.currentSubapp && this.currentSubapp instanceof SubApplication) {
      return this.currentSubapp;
    }

    // Destroy any previous subapplication if we can
    if (this.currentSubapp && this.currentSubapp.destroy) {
      this.currentSubapp.destroy();
    }

    // Run subapplication

    this.currentSubapp = new SubApplication({region: region});

    return this.currentSubapp;
  },


}

// for global events
_.extend(App, Backbone.Events);

module.exports = App;
