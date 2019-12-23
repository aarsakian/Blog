var gulp = require('gulp');
var $ = require('gulp-load-plugins')();

var browserify = require('browserify');
var watchify = require('watchify');
var jstify = require('jstify');

var htmlmin = require('gulp-htmlmin');
var sourcemaps = require('gulp-sourcemaps')
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var minifyStream = require('minify-stream')
var babelify = require('babelify');
var resolveDependencies = require('gulp-resolve-dependencies');
var concat = require('gulp-concat');

var browserSync = require('browser-sync');
var httpProxy = require('http-proxy');
var useref = require('gulp-useref');
var gulpif = require('gulp-if');
var minifyCss = require('gulp-clean-css');
var log = require('gulplog');
const terser = require('gulp-terser');

var workbox = require('workbox-build');




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
         return bundler.bundle().on('error', function(e){
            console.log(e);
         })
        .pipe(source('app.min.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .pipe(terser())
        .on('error', function(e){
            console.log(e);
         })
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('./blog/static/js/prod/'));
    };
    bundler.on('update', rebundle);
    bundler.on('log', log.info);
    bundler.on('error', $.util.log);
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
      .pipe(terser())
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
      .pipe(terser())
      .pipe(sourcemaps.init({loadMaps: true}))
        // Add transformation tasks to the pipeline here.
        .on('error', $.util.log)
      .pipe(sourcemaps.write('./'))
      .pipe(gulp.dest('./blog/static/js/prod/'));
  };

  bundler.on('update', rebundle);

  return rebundle();
});





gulp.task('html', function() {


  return gulp.src('blog/templates/base.html')
    .pipe(useref())
    .pipe(gulp.dest('blog/templates/rebase', {ext: '.html'}))
    .pipe(gulpif('*.css', minifyCss()))
    .pipe(gulp.dest('blog', {ext: '.css'}));
});

gulp.task('fonts', function () {
    return gulp.src([
        'blog/static/webfonts/*'])
        .pipe($.flatten())
        .pipe(gulp.dest('blog/static/fonts'));
})

gulp.task('minify-html', function() {
  return gulp.src([ 'blog/templates/*.html'
                  ])
    .pipe(htmlmin({collapseWhitespace: true, removeComments: true,
    processScripts:["text/x-handlebars.template"],
    collapseInlineTagWhitespace:true,
    collapseBooleanAttributes:true,
    minifyJS:true}))
    .pipe(gulp.dest('blog/templates/production'));
});


gulp.task('minify-html-rebase', function() {
  return gulp.src(['blog/templates/rebase/base.html'])
    .pipe(htmlmin({collapseWhitespace: true, removeComments: true,
    processScripts:["text/x-handlebars.template"],
    collapseInlineTagWhitespace:true,
    collapseBooleanAttributes:true,
    minifyJS:true}))
    .pipe(gulp.dest('blog/templates/production/rebase'));
});


gulp.task('generate-service-worker', () => {
  return workbox.generateSW({
    globDirectory: 'blog/static/js',
    globPatterns: [
      'prod/*min.js'

    ],
    swDest: 'blog/static/js/sw.js',
    clientsClaim: true,
    templatedURLs: {
        '/':  'blog/templates/production/index.html'

      },
    runtimeCaching: [{
    // Match any same-origin request that contains 'api'.
    urlPattern: '/api/*',
    // Apply a network-first strategy.
    handler: 'NetworkFirst',
    options: {
      // Fall back to the cache after 10 seconds.
      networkTimeoutSeconds: 10,
      // Use a custom cache name for this route.
      cacheName: 'my-api-cache',
      // Configure custom cache expiration.
      expiration: {
        maxEntries: 5,
        maxAgeSeconds: 60,
      },
      // Configure background sync.
      backgroundSync: {
        name: 'my-queue-name',
        options: {
          maxRetentionTime: 60 * 60,
        },
      },
      // Configure which responses are considered cacheable.
      cacheableResponse: {
        statuses: [0, 200],
        headers: {'x-test': 'true'},
      },
      // Configure the broadcast cache update plugin.
      broadcastUpdate: {
        channelName: 'my-update-channel',
      },
      // Add in any additional plugin logic you need.

      // matchOptions and fetchOptions are used to configure the handler.
      fetchOptions: {
        mode: 'no-cors',
      },
      matchOptions: {
        ignoreSearch: true,
      },

    },

  }],

    skipWaiting: true
  }).then(({warnings}) => {
    // In case there are any warnings from workbox-build, log them.
    for (const warning of warnings) {
      console.warn(warning);
    }
    console.info('Service worker generation completed.');
  }).catch((error) => {
    console.warn('Service worker generation failed:', error);
  });
});




gulp.task('browser-sync', function(done) {
    browserSync.init({
        open: 'external',
        proxy: "127.0.0.1:9082",
        port: 9082,
        host: "127.0.0.1",
        watch:true
        // port: 5000,


    });
    done();

    browserSync.watch([
        'blog/templates/*.html',
        'blog/**/*.css',
        'blog/**/*.js'
        ]).on('change', browserSync.reload);

});

gulp.task('serve-prod', gulp.series('browserify-crud-prod', 'browserify-general-prod', 'html', 'fonts',
                        'minify-html','minify-html-rebase', 'generate-service-worker', 'browser-sync'));


