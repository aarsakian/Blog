'use strict';


var Backbone = require('backbone');


var Notification  =  Backbone.Model.extend({
  title: "",
  message: "",
  icon: "",
  type:"",
  progress:"",
  url:"",
  target:""


});

module.exports = Notification;


