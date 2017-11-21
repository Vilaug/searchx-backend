var puppeteer = require('puppeteer');
var request = require('request');
var mongoose = require('mongoose');
var Document = require('../models/document');
var config = require('../config/config');

var refreshPeriod = 1000 * 60 * 60 * 24;


////


exports.processHtml = function(job, done) {
    var url = job.data.url;

    Document.findOne({'url': url}).exec()
        .then((doc) => {
            if (doc && doc.html) {
                var now = Math.floor(Date.now());
                var prev = Math.floor(doc.timestamp);
                if(now - prev < refreshPeriod) return done();
            }

            saveHtml(url)
                .then((result) => console.log('Document saved successfully : ' + url))
                .catch((err) => saveHtmlFallback(url))
                .then(() => done());
        });
};

exports.processScreenshot = function(job, done) {
    var url = job.data.url;

    Document.findOne({'url': url}).exec()
        .then((doc) => {
            if (!doc) return done();
            if (doc.screenshot) {
                var now = Math.floor(Date.now());
                var prev = Math.floor(doc.timestamp);
                if(now - prev < refreshPeriod) return done();
            }
            
            var id = doc._id;
            var filepath = config.imageDir + '/' + id + '.png';

            saveScreenshot(url, filepath)
                .then((result) => console.log('Document screenshot saved successfully : ' + url))
                .catch((err) => console.log('Failed to save screenshot : ' + err ))
                .then(() => done());
        });
};


////


var saveHtml = async function(url) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    await page.waitFor(100);

    const body = await page.content();
    upsertDocument(url, {
        'url': url,
        'html': body,
        'timestamp': Math.floor(Date.now())
    });

    await browser.close();
};

var saveHtmlFallback = function(url) {
    request(url, function (error, response, body) {
        upsertDocument(url, {
            'url': url,
            'html': body,
            'timestamp': Math.floor(Date.now())
        })
    });
}

var saveScreenshot = async function(url, filepath) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url, {waitUntil: 'networkidle2'});
    await page.setViewport({width: 1360, height: 768});
    await page.waitFor(100);

    await page.screenshot({fullPage: true, path: filepath});
    upsertDocument(url, {
        'url': url,
        'screenshot': filepath,
        'timestamp': Math.floor(Date.now())
    });

    await browser.close();
};


////


var upsertDocument = function(url, doc) {
    var query = {'url': url};
    var options = {
        upsert: true,
        new: true,
        setDefaultsOnInsert: true
    }

    Document.findOneAndUpdate(query, doc, options, function(err, res) {
        if (err) {
            console.log('Could not save document.');
            console.log(err);
        }
    });
}