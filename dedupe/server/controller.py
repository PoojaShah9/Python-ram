from future.builtins import next
from flask import jsonify,json
from itertools import combinations, groupby
import os
import csv
import re
import collections
import logging
import optparse
from numpy import nan
import datetime
from elasticsearch import Elasticsearch

import dedupe
from unidecode import unidecode

input_file = 'inputfile/input.csv'

settings_file = 'myTest_learned_settings'
training_file = 'myTest_training.json'

now = datetime.datetime.now()

host = 'search-dedupe-n3y3uvp2uoiok2jgubwotjwag4.us-east-1.es.amazonaws.com'

inputfile = 'example.csv'

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True
)




def firstcall():

  import dedupe
  data_d = readData(input_file)

  variables = [{'field' : 'name', 'type': 'String'},
               {'field' : 'address', 'type': 'String'},
               {'field' : 'city', 'type': 'String', 'has missing':True},
               {'field' : 'cuisine', 'type': 'String', 'has missing':True}]

  deduper = dedupe.Dedupe(variables)
  deduper.sample(data_d, 150000, .5)

  return [deduper,data_d]

def preProcess(column):

    import unidecode
    #column = column.decode("utf8")
    column = unidecode.unidecode(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column :
        column = None
    return column

def readData(filename):

    data = []
    if es.indices.exists(index="inputdata"):
        res = es.search(index="inputdata", doc_type='data', body={"query": {"match": {"filename" : inputfile}}})
        data = res['hits']['hits'][0]['_source']['data']

    data_d = {}
    reader = csv.DictReader(data)
    for row in reader:
        clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
        row_id = int(row['unique_id'])
        data_d[row_id] = dict(clean_row)

    return data_d

def firstprogram():

    import dedupe
    # 1

    deduper = firstcall()[0]
    pair = deduper.uncertainPairs()
    return jsonify({'result' : pair[0]})

def secondprogram(jsonfile):

    #2
    import dedupe
    deduper = firstcall()[0]
    data_d = firstcall()[1]
    newinputs = jsonfile
    newJson = {'distinct':[],'match':[]}
    for dist in enumerate(newinputs['distinct']):
        abc = list(dist)
        xyz = tuple(abc[1])
        newJson['distinct'].append(xyz)

    for dist in enumerate(newinputs['match']):
        abc = list(dist)
        xyz = tuple(abc[1])
        newJson['match'].append(xyz)

    labeled_examples = newJson
    deduper.markPairs(labeled_examples)

    deduper.train()

    with open(training_file, 'w') as tf :
            deduper.writeTraining(tf)

    threshold = deduper.threshold(data_d, recall_weight=2)

    clustered_dupes = deduper.match(data_d, threshold)

    cluster_membership = {}
    cluster_notmember = {}
    cluster_id = 0
    for (cluster_id, cluster) in enumerate(clustered_dupes):
        id_set, scores = cluster
        """
        id_tuple = list(id_set)
        cluster_notmember[id_tuple[1]] = {}
        id_tuple.pop()
        id_set = tuple(id_tuple)
        scores_tuple = list(scores)
        scores_tuple.pop()
        scores = tuple(scores_tuple)
        """
        cluster_d = [data_d[c] for c in id_set]
        canonical_rep = dedupe.canonicalize(cluster_d)
        for record_id, score in zip(id_set, scores) :
            cluster_membership[record_id] = {
                "cluster id" : cluster_id,
                "canonical representation" : canonical_rep,
                "confidence": score
            }

    singleton_id = cluster_id + 1

    result = []
    out = inputfile.split('.')
    output_file = 'OP' + out[0] + '.csv'
    with open(output_file, 'w') as f_output:
        writer = csv.writer(f_output)

        with open(input_file) as f_input :
            reader = csv.reader(f_input)

            heading_row = next(reader)
            heading_row.insert(0, 'confidence_score')
            heading_row.insert(0, 'Cluster ID')
            canonical_keys = canonical_rep.keys()
            for key in canonical_keys:
                heading_row.append('canonical_' + key)

            writer.writerow(heading_row)

            for row in reader:
                row_id = int(row[0])
                if row_id in cluster_membership :
                    cluster_id = cluster_membership[row_id]["cluster id"]
                    canonical_rep = cluster_membership[row_id]["canonical representation"]
                    row.insert(0, cluster_membership[row_id]['confidence'])
                    row.insert(0, cluster_id)
                    for key in canonical_keys:
                        row.append(canonical_rep[key].encode('utf8'))
                elif row_id not in cluster_notmember :
                    row.insert(0, None)
                    row.insert(0, singleton_id)
                    singleton_id += 1
                    for key in canonical_keys:
                        row.append(None)
                writer.writerow(row)
                result.append(row)

    return (output_file)
