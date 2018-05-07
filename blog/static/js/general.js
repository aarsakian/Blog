'user strict';
var $ = require('jquery');
require('jquery-typeahead');

$(document).ready(function() {



     var actify=function (url){

        $('.nav-item').each(function(){
	    $(this).removeClass('active');
            var link=$(this).children().first()[0].pathname;

            if (url===link){
                $(this).addClass('active');}

            });
      }


   var  url=location.pathname;
   actify(url);


$.typeahead({
    input: '.js-typeahead-country_v1',
    order: "desc",
    source: {
        data: [
            "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda",
            "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
            "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia",
            "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burma",
            "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Republic", "Chad",
            "Chile", "China", "Colombia", "Comoros", "Congo, Democratic Republic", "Congo, Republic of the",
            "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti",
            "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador",
            "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Gabon",
            "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Greenland", "Grenada", "Guatemala", "Guinea",
            "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India",
            "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan",
            "Kazakhstan", "Kenya", "Kiribati", "Korea, North", "Korea, South", "Kuwait", "Kyrgyzstan", "Laos",
            "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
            "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
            "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Morocco", "Monaco",
            "Mozambique", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
            "Nigeria", "Norway", "Oman", "Pakistan", "Panama", "Papua New Guinea", "Paraguay", "Peru",
            "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Samoa", "San Marino",
            "Sao Tome", "Saudi Arabia", "Senegal", "Serbia and Montenegro", "Seychelles", "Sierra Leone",
            "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "Spain",
            "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan",
            "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey",
            "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
            "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
        ]
    },
    callback: {
        onInit: function (node) {
            console.log('Typeahead Initiated on ' + node.selector);
        }
    }
});
   
   /* var map = {}
    $('.typeahead').typeahead({
        minLength: 3,
        order: "asc",
        updater: function(item) {
            return item;
        },
   
    source: function (query,process) {
          console.log("QUREYT"+query)
          $.get('/search', { query:query}, function (data) {
            titlesbodies = [];
            $.each(data.data, function (i, post) {
               titlesbodies.push(post.body);
               titlesbodies.push(post.title);
               map[post.title] = post;
               map[post.body]= post;
           });
              process(titlesbodies);
             
        });
   },
   afterSelect: function(item){
     var post = map[item];
     if (typeof post !== "undefined") 
       window.location =  "/"+post.category+"/"+post.year+"/"+post.month+"/"+post.title;
     } 
  
  });



*/
});