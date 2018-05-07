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

var browserSync = require('browser-sync');
var httpProxy = require('http-proxy');

var reload = browserSync.reload;


// Bundle files with browserify
gulp.task('browserify-crud', () => {
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
            .pipe(source('app.min.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/tmp/'));
  };

  bundler.on('update', rebundle);

  return rebundle();
});

gulp.task('browserify-general', () => {
// set up the browserify instance on a task basis
    var bundler = browserify({
    entries: 'blog/static/js/general.js',
    debug: true,
// defining transforms here will avoid crashing your stream
    transform: [jstify]
    });

     bundler = watchify(bundler);

     var rebundle = function() {
          return bundler.bundle()
            .on('error', $.util.log)
            .pipe(source('general.min.js'))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/tmp/'));
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





gulp.task('serve', ['browserify-crud', 'browserify-general'], () => {
  var serverProxy = httpProxy.createProxyServer();

  browserSync({
    port: 9000,
    ui: {
      port: 9001
    },
    server: {
      baseDir: ['./blog'],
      middleware: [
        function (req, res, next) {
          if (req.url.match(/.*/)) {
            serverProxy.web(req, res, {
              target: 'http://localhost:9082'
            });
          } else {
            next();
          }
        }
      ]
    }
  });

  gulp.watch([
    'blog/templates/*.html',
    'blog/**/*.css',
    'blog/**/*.js'
  ]).on('change', reload);
});
