"use strict";

const fs = require("fs");
const bing = require("./providers/bing");

const { MongoClient } = require("mongodb");

const config = require("../../config/config");
const dbName = "aggregated-search";

const client = new MongoClient(config.db, { useUnifiedTopology: true });

const PREPROCESSED = "preprocessed";
const VERTICAL_WEBSITES = "retrieved_vertical_websites";
const QUERY_WEBSITES = "retrieved_query_websites";
const IMPORTED_VERTICALS = "imported_verticals";
const IMPORTED_QUERIES = "imported_queries";
const VERTICAL_DOCUMENTS = "retrieved_vertical_documents";
const QUERY_DOCUMENTS = "retrieved_query_documents";

exports.retrieveWebsites = async function () {
    await client.connect();
    if (!(await getConfigOption(IMPORTED_VERTICALS))) {
        console.log("Verticals not imported, importing");
        importVerticals();
    }
    console.log("Verticals imported");

    if (!(await getConfigOption(IMPORTED_QUERIES))) {
        console.log("Queries not imported, importing");
        importQueries();
    }
    console.log("Queries imported");

    if (!(await getConfigOption(VERTICAL_WEBSITES))) {
        console.log("Vertical websites not retrieved, retrieving");
        retrieveVerticalWebsites(100);
    }
    console.log("Vertical results retrieved");

    if (!(await getConfigOption(QUERY_WEBSITES))) {
        console.log("Query websites not retrieved, retrieving");
        retrieveQueryWebsites(50);
    }
    console.log("Query results retrieved");
};

async function getConfigOption(option) {
    const config = await client.db(dbName).collection("config").findOne();
    if (!Object.keys(config).length == 0) {
        return config[option];
    } else {
        await client
            .db(dbName)
            .collection("config")
            .insertOne({
                [VERTICAL_WEBSITES]: false,
                [QUERY_WEBSITES]: false,
                [IMPORTED_QUERIES]: false,
                [IMPORTED_VERTICALS]: false,
                [PREPROCESSED]: false,
                [VERTICAL_DOCUMENTS]: false,
                [QUERY_DOCUMENTS]: false,
            });
        return false;
    }
}

async function setConfigOption(option, value) {
    await client
        .db(dbName)
        .collection("config")
        .updateOne(
            { _id: await getConfigOption("_id") },
            { $set: { [option]: value } }
        );
}

async function readCollection(collectionName) {
    const collection = client.db(dbName).collection(collectionName);
    const cursor = collection.find();

    if ((await cursor.count()) === 0) {
        console.log(
            "No documents found in %s were found!".replace("%s", collectionName)
        );
    }

    return await cursor.toArray();
}

async function importVerticals() {
    let split = fs
        .readFileSync("data/verticals_fedweb2014.txt", "utf-8", (err, data) => {
            if (err) {
                console.log(err);
            }
        })
        .split("\n");
    const collection = await client.db(dbName).collection("verticals");
    for (let i = 0; i < split.length; i++) {
        let labeled_vertical = split[i].split("\t");
        if (labeled_vertical.length == 2) {
            await collection.insertOne({
                vertical_label: labeled_vertical[0],
                vertical_name: labeled_vertical[1],
            });
        }
    }
    setConfigOption(IMPORTED_VERTICALS, true);
}

async function importQueries() {
    let split = fs
        .readFileSync(
            "data/queryterms_fedweb2014.txt",
            "utf-8",
            (err, data) => {
                if (err) {
                    console.log(err);
                }
            }
        )
        .split("\n");
    const collection = await client.db(dbName).collection("queries");
    for (let i = 0; i < split.length; i++) {
        let labeled_query = split[i].split("\t");
        if (labeled_query.length == 2) {
            await collection.insertOne({
                query_label: labeled_query[0],
                query: labeled_query[1],
            });
        }
    }
    setConfigOption(IMPORTED_QUERIES, true);
}

async function retrieveVerticalWebsites(n) {
    const vertical_websites = client.db(dbName).collection("vertical-websites");
    let queries_json = fs.readFileSync(
        "data/queries.json",
        "utf-8",
        (err, data) => {
            if (err) {
                console.log(err);
            }
        }
    );
    let vertical_queries = JSON.parse(queries_json);
    let verticals = Object.keys(vertical_queries);
    for (let i = 0; i < verticals.length; i++) {
        for (let j = 0; j < vertical_queries[verticals[i]].length; j++) {
            let query = vertical_queries[verticals[i]][j];
            for (let k = 1; k <= n / 10; k++) {
                let responseData = await bing.fetch(query, "web", k, 10);
                responseData.results.forEach(async function (result) {
                    await vertical_websites.insertOne({
                        vertical_name: verticals[i],
                        query: query,
                        website: result.url,
                    });
                });
            }
        }
        console.log("Retrieved for " + verticals[i]);
    }
    setConfigOption(VERTICAL_WEBSITES, true);
}

async function retrieveQueryWebsites(n) {
    const query_websites = client.db(dbName).collection("query-websites");
    let queries = await readCollection("queries");
    for (let i = 0; i < queries.length; i++) {
        let query = queries[i]["query"];
        for (let k = 1; k <= n / 10; k++) {
            let responseData = await bing.fetch(query, "web", k, 10);
            responseData.results.forEach(async function (result) {
                await query_websites.insertOne({
                    query: query,
                    website: result.url,
                });
            });
        }
        console.log("Retrieved for " + query);
    }
    setConfigOption(QUERY_WEBSITES, true);
}

async function readCollection(collectionName) {
    const collection = client.db(dbName).collection(collectionName);
    const cursor = collection.find();

    if ((await cursor.count()) === 0) {
        console.log(
            "No documents found in %s were found!".replace("%s", collectionName)
        );
    }

    return await cursor.toArray();
}
