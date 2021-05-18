import argparse


def get_training_data_cli_parser():
    parser = argparse.ArgumentParser(description='Download, label, and preprocess training data. '
                                                 'Data will be taken from websites returned from querying www.odp.org. '
                                                 'Queries and labels will be verticals names. '
                                                 'Vertical names are taken from TREC 2014 FedWeb track. '
                                                 'Text from websites will be preprocessed using Stanford Core NLP')
    parser.add_argument('-n', type=int,
                        help='Number of websites that will be retrieved from www.odp.org for each vertical',
                        default=100)
    return parser
