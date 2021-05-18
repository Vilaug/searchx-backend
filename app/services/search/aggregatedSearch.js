"use strict";

var synonyms = require("synonyms");

const verticals = ["images", "news", "videos"];

const Inflectors = require("en-inflectors").Inflectors;
const fs = require("fs");
const bing = require("./providers/bing");

exports.findRelevantVerticals = function (query) {
    const stringVerticals = stringFeature(query);
    const categoryVerticals = categoryFeature(query);
};

function parseVerticals() {
    let split = fs
        .readFileSync("data/verticals_fedweb2014.txt", "utf-8", (err, data) => {
            if (err) {
                console.log(err);
            }
        })
        .split("\n");
    var labeled_verticals = {};
    for (let i = 0; i < split.length; i++) {
        let labeled_vertical = split[i].split("\t");
        if (labeled_vertical.length > 1) {
            labeled_verticals[labeled_vertical[0]] = labeled_vertical[1];
        }
    }
    return labeled_verticals;
}

async function saveVerticalWebsites(labeled_verticals, n) {
    let vertical_labels = Object.keys(labeled_verticals);
    let vertical_websites = {};
    console.log("Started retrieving");
    for (let i = 0; i < vertical_labels.length; i++) {
        let websites = [];
        for (let k = 1; k <= n / 10; k++) {
            let responseData = await bing.fetch(
                labeled_verticals[vertical_labels[i]],
                "web",
                k,
                10
            );
            responseData.results.forEach(function (result) {
                websites.push(result);
            });
        }
        vertical_websites[labeled_verticals[vertical_labels[i]]] = websites;
        console.log("Retrieved for " + labeled_verticals[vertical_labels[i]]);
    }
    console.log("Started saving");
    fs.writeFileSync(
        "data/vertical_websites.json",
        JSON.stringify(vertical_websites),
        (err) => {
            if (err) throw err;
            console.log("The file has been saved!");
        }
    );
    return vertical_websites;
}

function categoryFeature(query) {
    const verticalWebsites = readOrRetrieveWebsites();
}

function readOrRetrieveWebsites() {
    let vertical_websites = readWebsites();
    if (!vertical_websites) {
        const labeled_verticals = parseVerticals();
        vertical_websites = saveVerticalWebsites(labeled_verticals, 100);
    }
}

function readWebsites() {
    return JSON.parse(
        fs.readFileSync("data/vertical_websites.json", "utf-8", (err, data) => {
            if (err) {
                console.log(err);
            }
        })
    );
}

function stringFeature(query) {
    const queryWords = query.split(" ");
    const verticalRules = getVerticalRules();
    let verticalBinary = [];
    verticals.forEach(function () {
        verticalBinary.push(false);
    });
    for (let i = 0; i < queryWords.length; i++) {
        const word = queryWords[i];
        const inflectorInstance = new Inflectors(word);
        for (let j = 0; j < verticals.length; j++) {
            const currentVertical = verticals[j];
            const verticalSynonyms = verticalRules[currentVertical];
            for (
                let k = 0;
                k < verticalSynonyms.length && !verticalBinary[j];
                k++
            ) {
                const currentSyn = verticalSynonyms[k];
                if (currentSyn.includes(word) || word.includes(currentSyn)) {
                    verticalBinary[j] = true;
                } else if (inflectorInstance.isPlural()) {
                    let singularWord = inflectorInstance.toSingular();
                    if (
                        singularWord.includes(currentSyn) ||
                        currentSyn.includes(singularWord)
                    ) {
                        verticalBinary[j] = true;
                    }
                }
            }
        }
    }
    return verticalBinary;
}

function getVerticalRules() {
    return {
        images: [
            "image",
            "picture",
            "icon",
            "photograph",
            "photo",
            "portrait",
            "pic",
            "img",
        ],
        news: ["news", "article"],
        videos: ["video", "recording"],
    };
}
