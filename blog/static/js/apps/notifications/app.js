'user strict';

var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;
var Notification = require('./models/notification')


class NotificationLayout extends Layout {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#notification-layout';
    this.regions = {
      messages: '.notification-messages'


    };
  }

}


class NotificationView extends ModelView {
  constructor(options) {
    super(options);
    this.template = '#notifications-template';

    this.model = new Notification({});

  }


  initialize(options) {
    this.listenTo(this.model, 'change', this.render);

  //  var tagList = new TagListView({collection: options.model.tags});

  }

  showMessage(msg) {
      console.log("NOTF"+this.model);
      this.model.set("message", msg);
  }

}


class Notifier {
  constructor(options) {

    // Region where the application will be placed
     this.region = options.region;

    // Allow subapplication to listen and trigger events,
    // useful for subapplication wide events
    _.extend(this, Backbone.Events);
  }


  showSuccessMessage(msg) {

      layout = new NotificationLayout();
      this.region.show(layout);

      var notificationView = new NotificationView({model: new Notification({message:msg})});

      layout.getRegion('messages').show(notificationView);

  }

  destroy() {
    this.region.remove();
    this.stopListening();
  }
}


module.exports = NotificationView;