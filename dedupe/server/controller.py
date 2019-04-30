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
import boto3

import dedupe
from unidecode import unidecode

settings_file = 'myTest_learned_settings'
training_file = 'myTest_training.json'

now = datetime.datetime.now()

host = 'search-dedupe-n3y3uvp2uoiok2jgubwotjwag4.us-east-1.es.amazonaws.com'

s3 = boto3.resource('s3',aws_access_key_id='AKIAWQGV4HBLW42U7EUL',aws_secret_access_key='riihGrGkiIGHW0kqKSeBsvEW4M7cS3VpzAJMXSOa')
bucket = s3.Bucket(u'pythoncsv')

inputfile = 'example5.csv'

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True,
    request_timeout=200000
)

data_d = {}
deduper = ''


def firstcall():

  import dedupe
  global data_d
  global deduper

  data_d = readData(inputfile)
  variables = [{'field' : 'NPI', 'type': 'ShortString'},
               {'field' : 'PECOS_ASCT_CNTL_ID', 'type': 'ShortString'},
               {'field' : 'ENRLMT_ID', 'type': 'ShortString'},
               {'field' : 'PROVIDER_TYPE_CD', 'type': 'ShortString'},
               {'field' : 'PROVIDER_TYPE_DESC', 'type': 'ShortString'},
               {'field' : 'STATE_CD', 'type': 'ShortString'},
               {'field' : 'ORG_NAME', 'type': 'ShortString'},
               {'field' : 'GNDR_SW', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_LINE_1_TXT', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_LINE_2_TXT', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_CITY_NAME', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_STATE_CD', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_ZIP_CD', 'type': 'ShortString'},
               {'field' : 'PRVDR_ADR_ZIP_PLUS_4_CD', 'type': 'ShortString'},
               {'field' : 'TEL_NUM', 'type': 'ShortString'},
               {'field' : 'FIRST_NAME', 'type': 'ShortString'},
               {'field' : 'LAST_NAME', 'type': 'ShortString'},
               {'field' : 'MDL_NAME', 'type': 'ShortString'}]

  deduper = dedupe.Dedupe(variables)
  deduper.sample(data_d, 100,0.5)

  return [deduper,data_d]

def preProcess(column):


    import unidecode
    column = column.decode("utf8")
    column = unidecode.unidecode(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column :
        column = None
    return column

def readData(filename):

    global data_d
    global deduper

    data = []
    if es.indices.exists(index="inputdata"):
        res = es.search(index="inputdata", body={"query": {"match": {"filename" : inputfile}}})
        data = res['hits']['hits'][0]['_source']['data']

    reader = csv.DictReader(data)
    for row in reader:
        clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
        row_id = int(row['unique_id'])
        data_d[row_id] = dict(clean_row)

    return data_d


def newDataD():
    data_d = {}

    obj = bucket.Object(key='input.csv')
    response = obj.get()
    lines = response[u'Body'].read().splitlines()
    reader = csv.reader(lines)

    for row in reader:
        clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
        row_id = int(row['unique_id'])
        data_d[row_id] = dict(clean_row)

    return data_d

def firstprogram():

    import dedupe
    # 1
    global data_d
    global deduper

    if(data_d == {}):
      deduper = firstcall()[0]
    pair = deduper.uncertainPairs()
    return jsonify({'result' : pair[0]})

def secondprogram(jsonfile):

    #2
    import dedupe
    global data_d
    global deduper

    if(data_d == {}):
      mydata = firstcall()
      deduper = mydata[0]

    data_d = newDataD()
    print(len(data_d.keys()))
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
    count = 0;

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
        count += 1
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

        obj = bucket.Object(key='input.csv')
        response = obj.get()
        lines = response[u'Body'].read().splitlines()
        reader = csv.reader(lines)

        print('online reading done')
        heading_row = next(reader)
        heading_row.insert(0, 'confidence_score')
        heading_row.insert(0, 'Cluster ID')
        canonical_keys = canonical_rep.keys()
        for key in canonical_keys:
            heading_row.append('canonical_' + key)

        writer.writerow(heading_row)

        for row in reader:
            print('reading row')
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

    data_d = {}
    deduper = ''
    return [output_file,count]
