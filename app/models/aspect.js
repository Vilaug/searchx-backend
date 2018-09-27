'use strict';

const mongoose = require('mongoose');
const Schema   = mongoose.Schema;

const AspectSchema = new Schema({
    userId: {
        type: String,
        required: true
    },
    sessionId: {
        type: String,
        required: true
    },
    aspects: {
        type: Array,
        required: true
    },
    novelty: {
        type: Map,
        require: true
    },
    centroidvectors : {
        type: Map
    }
});

module.exports = mongoose.model('Aspect', AspectSchema);
