'use strict';

var Backbone = require('backbone');

var Image =  Backbone.Model.extend({
    url:null,
    filename:null
});
module.exports = Image;