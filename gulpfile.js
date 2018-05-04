var gulp = require('gulp');
var $ = require('gulp-load-plugins')();

var browserify = require('browserify');
var watchify = require('watchify');
var jstify = require('jstify');

var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var sourcemaps = require('gulp-sourcemaps');

var resolveDependencies = require('gulp-resolve-dependencies');
var concat = require('gulp-concat');



// Bundle files with browserify
gulp.task('browserify', () => {
// set up the browserify instance on a task basis
    var bundler = browserify({
    entries: 'blog/static/js/main.js',
    debug: true,
// defining transforms here will avoid crashing your stream
    transform: [jstify]
    });

     bundler = watchify(bundler);

     var rebundle = function() {
          return bundler.bundle()
            .on('error', $.util.log)
            .pipe(source('blog/static/js/app.min.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('blog/static/maps'))
      .pipe(gulp.dest('blog/static/js'));
  };

  bundler.on('update', rebundle);

  return rebundle();
});

gulp.task('js', function(){
  gulp.src(['blog/static/js/blog/static/js/app.min.js'])
    .pipe(resolveDependencies({
      pattern: /\* @requires [\s-]*(.*\.js)/g
    }))
        .on('error', function(err) {
            console.log(err.message);
        })
    .pipe(concat('app.min.js'))
    .pipe(gulp.dest('dests.js'));
});



