'user strict';

var _ = require('underscore');
var Backbone = require('backbone');
var App = require('../../app');
var Layout = require('../../common').Layout;
var ModelView = require('../../common').ModelView;
var Notification = require('./models/notification')




class NotificationView extends ModelView {
  constructor(options) {
    super({tagName:"div", className:"row col-12"});

    this.template = '#notifications-template';

  }

  showMessage(msg, type) {
      this.model = new Notification({"message":msg,
                                    "type":type});

      var view  = this.render();
      this.fadeMessage();

  }

  fadeMessage() {

    var view = this;
    this.$(".alert").fadeTo(2000, 500).slideUp(500, function(){
        view.$(".alert").slideUp(500);
    });

  }


}




module.exports = NotificationView;