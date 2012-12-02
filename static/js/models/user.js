(function (models){
    models.User=Backbone.Model.extend({
        defaults:{
        
        
        },
        url:"user",
        //parse:function(data){
        ////    console.log(data.user_admin);
        //    return data.user_status;
        //},
        
    });
})(app.models);