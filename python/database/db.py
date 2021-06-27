class DB:
    def __init__(self, database):
        self.database = database
        self.queries = ["7015", "7044", "7045", "7072", "7092", "7111", "7123", "7137", "7146", "7161", "7167", "7173",
                        "7174", "7176", "7185", "7194", "7197", "7200", "7205", "7207", "7211", "7212", "7215", "7216",
                        "7230", "7235", "7236", "7239", "7242", "7249", "7250", "7252", "7261", "7263", "7274", "7293",
                        "7299", "7303", "7307", "7320", "7326", "7328", "7431", "7441", "7448", "7486", "7491", "7501",
                        "7015", "7044", "7045", "7092", "7111", "7123", "7137", "7146", "7161", "7167", "7173", "7174",
                        "7176", "7185", "7194", "7197", "7200", "7205", "7207", "7211", "7212", "7215", "7216", "7222",
                        "7230", "7235", "7236", "7239", "7242", "7249", "7250", "7252", "7261", "7263", "7274", "7293",
                        "7299", "7303", "7307", "7320", "7326", "7328", "7431", "7441", "7448", "7486", "7491",
                        "7501", "7222", "7265"]

    def get_vertical_text_list(self):
        return list(map(lambda x: [x['text'], x['meta_description']],
                        self.database['vertical-data'].find().sort('_id')))

    def get_vertical_list(self):
        return list(map(lambda x: x['vertical_name'],
                        self.database['vertical-data'].find({}, {'_id': 0, 'vertical_name': 1}).sort('_id')))

    def get_query_text_list(self, query):
        return list(map(lambda x: [x['text'], x['meta_description']],
                        self.database['query-data'].find({'query': query}).sort('_id')))

    def get_queries(self):
        return self.database['queries'].find({"query_label": {"$in": self.queries}}).sort('query_label')

    def get_vertical_label(self, vertical_name):
        return self.database['verticals'].find_one({'vertical_name': vertical_name}, {'_id': 0, 'vertical_label': 1})[
            'vertical_label']
