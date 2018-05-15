var gulp = require('gulp');
var $ = require('gulp-load-plugins')();

var browserify = require('browserify');
var watchify = require('watchify');
var jstify = require('jstify');

var htmlmin = require('gulp-htmlmin');

var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var sourcemaps = require('gulp-sourcemaps');
var babelify = require('babelify');
var resolveDependencies = require('gulp-resolve-dependencies');
var concat = require('gulp-concat');

var browserSync = require('browser-sync');
var httpProxy = require('http-proxy');
var useref = require('gulp-useref');
var gulpif = require('gulp-if');
var minifyCss = require('gulp-clean-css');

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


// Bundle files with browserify
gulp.task('browserify-crud-prod', () => {
// set up the browserify instance on a task basis
    var bundler = browserify({
    entries: 'blog/static/js/main.js',
    debug: true,
// defining transforms here will avoid crashing your stream
    transform: [babelify, jstify]
    });

     bundler = watchify(bundler);

     var rebundle = function() {
          return bundler.bundle()
            .on('error', $.util.log)
            .pipe(source('app.min.js'))
      .pipe(buffer())
      .pipe($.uglify()).on('error', function(e){
            console.log(e);
         })
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/prod/'));
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
    transform: [ jstify]
    });

     bundler = watchify(bundler);

     var rebundle = function() {
          return bundler.bundle()
            .on('error', $.util.log)
            .pipe(source('general.min.js'))
      .pipe(buffer()).on('error', function(e){
            console.log(e);
         })
      .pipe($.uglify())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/tmp/'));
  };

  bundler.on('update', rebundle);

  return rebundle();
});


gulp.task('browserify-general-prod', () => {
// set up the browserify instance on a task basis
    var bundler = browserify({
    entries: 'blog/static/js/general.js',
    debug: true,
// defining transforms here will avoid crashing your stream
    transform: [babelify, jstify]
    });

     bundler = watchify(bundler);

     var rebundle = function() {
          return bundler.bundle()
            .on('error', $.util.log)
            .pipe(source('general.min.js'))
      .pipe(buffer()).on('error', function(e){
            console.log(e);
         })
      .pipe($.uglify())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/prod/'));
  };

  bundler.on('update', rebundle);

  return rebundle();
});


gulp.task('js-resolve', function(){
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


gulp.task('html', function() {


  return gulp.src('blog/templates/base.html')
    .pipe(useref())
    .pipe(gulp.dest('blog/templates/rebase', {ext: '.html'}))
    .pipe(gulpif('*.css', minifyCss()))
    .pipe(gulp.dest('blog', {ext: '.css'}));
});

gulp.task('fonts', function () {ba
    return gulp.src([
        'blog/static/webfonts/*'])
        .pipe($.flatten())
        .pipe(gulp.dest('blog/static/fonts'));
})

gulp.task('minify-html', function() {
  return gulp.src('blog/templates/**/*.html')
    .pipe(htmlmin({collapseWhitespace: true}))
    .pipe(gulp.dest('blog/templates/production'));
});


gulp.task('serve-prod', ['browserify-crud-prod', 'browserify-general-prod', 'html', 'fonts',
                        'minify-html'], () => {
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
