const {src, dest, watch, series} = require('gulp');
const concat = require('gulp-concat');

function scripts() {
    return src([
        'node_modules/jquery/dist/jquery.js',
        'node_modules/bootstrap/dist/js/bootstrap.bundle.js',
        './static/js/develop.js'])
        .pipe(concat('main.js'))
        .pipe(dest('./static/js/'));
}

function styles() {
    return src(['node_modules/bootstrap/dist/css/bootstrap.css', './static/css/develop.css'])
        .pipe(concat('main.css'))
        .pipe(dest('./static/css/'));
}

function watchAssets() {
    watch(['static/js/develop.js'], scripts);
    watch(['static/css/develop.css'], styles);
}

exports.scripts = scripts;
exports.styles = styles;

exports.watch = series(scripts, styles, watchAssets);