from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
import boto3
import uuid
import csv
import json

from elasticsearch import Elasticsearch



from future.builtins import next

import os
import csv
import re
import collections
import logging
import optparse
from numpy import nan

import dedupe
from unidecode import unidecode

app = Flask(__name__)
CORS(app)

fields = []
rows = []

filepath = os.getcwd() + '/inputfile'

if not os.path.exists(filepath):
    os.makedirs(filepath)

s3client = boto3.client('s3',aws_access_key_id='AKIAWQGV4HBLW42U7EUL',aws_secret_access_key='riihGrGkiIGHW0kqKSeBsvEW4M7cS3VpzAJMXSOa')
s3client.download_file('pythoncsv','example.csv', 'input.csv')

host = 'search-dedupe-n3y3uvp2uoiok2jgubwotjwag4.us-east-1.es.amazonaws.com'
from controller import firstprogram,secondprogram

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True
)
print(es.info())

@app.route('/inputelastic', methods=['PUT'])
def input():
    print('input')
    doc = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': "datetime.now()",
    }

    res = es.index(index="test-index", doc_type='tweet', body=doc)
    #res = es.indices.create('test', body=doc)

    return jsonify({'result' : res['result']})

@app.route('/getelastic', methods=['GET'])
def search():
    res = es.search(index="csvresult", doc_type='records')

    return jsonify({'result' : res['hits']['hits']})

@app.route('/getcsv', methods=['GET'])
def get_stars():
  output = []
  count = 0;
  header = []
  with open('input.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        if count == 0:
            count = 1
            for single in row:
                header.append(single)
        else:
            final = {}
            for index, item in enumerate(header):
                 final[item]= row[index]
            output.append(final)

  return jsonify({'result' : output})

@app.route('/getquestions', methods=['GET'])
def get_questions():
    questions = firstprogram()
    return questions

@app.route('/getnewcsv', methods=['POST'])
def get_downloadcsv():
    d = json.loads(request.data)
    jsonfile = d['final']
    xyz = secondprogram(jsonfile)
    output = []
    count = 0;
    header = []
    with open(xyz) as csvfile:
      readCSV = csv.reader(csvfile, delimiter=',')
      for row in readCSV:
          if count == 0:
              count = 1
              for single in row:
                  header.append(single)
          else:
              final = {}
              for index, item in enumerate(header):
                   final[item]= row[index]
              output.append(final)

    doc = {'result' : output}
    print(doc)
    res = es.index(index="csvresult", doc_type='records', body=doc)
    return jsonify({'result' : output})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
