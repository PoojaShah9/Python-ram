from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
import boto3

from elasticsearch import Elasticsearch

from controller import firstprogram,secondprogram

import os
import csv
import re
import json

import dedupe
from unidecode import unidecode

app = Flask(__name__)
CORS(app)

fields = []
rows = []

inputfile = 'example4.csv'

"""
filepath = os.getcwd() + '/inputfile'

if not os.path.exists(filepath):
    os.makedirs(filepath)
"""

#s3client = boto3.client('s3',aws_access_key_id='AKIAWQGV4HBLW42U7EUL',aws_secret_access_key='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')
#s3client.download_file('pythoncsv',inputfile, filepath + '/input.csv')

host = 'search-dedupe-n3y3uvp2uoiok2jgubwotjwag4.us-east-1.es.amazonaws.com'

s3 = boto3.resource('s3',aws_access_key_id='AKIAWQGV4HBLW42U7EUL',aws_secret_access_key='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')
bucket = s3.Bucket(u'pythoncsv')


es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    use_ssl=True,
    verify_certs=True,
    request_timeout=1300
)
print(es.info())

@app.route('/inputelastic', methods=['PUT'])
def input():
    doc = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': "datetime.now()",
    }

    res = es.index(index="test-index", doc_type='tweet', body=doc)
    return jsonify({'result' : res['result']})

@app.route('/getelastic', methods=['GET'])
def search():
    res = es.search(index="csvresult")

    return jsonify({'result' : res['hits']['hits']})

@app.route('/getcsv', methods=['GET'])
def get_stars():
  output = []
  count = 0;
  header = []
  update = 'false'
  id = 'undefined'
  if es.indices.exists(index="inputdata"):
      res = es.search(index="inputdata", body={"query" : {"term" : { "filename": inputfile } }})
      id = res['hits']['hits'][0]['_id'] if (len(res['hits']['hits']) > 0)  else 'undefined'

  if id != 'undefined':
    update = 'true'

  obj = bucket.Object(key=inputfile)
  response = obj.get()
  lines = response[u'Body'].read().splitlines()
  readCSV = csv.reader(lines)
  doc = {
      'filename': inputfile,
      'data': lines,
  }
  print(update,id)
  if update == 'false':
    es.index(index="inputdata", doc_type='data', body=doc)
  #else:
  #  es.index(index='inputdata',doc_type='data',id=id,body=doc)

  for index, row in enumerate(readCSV):
    	if count == 0:
  	  count = 1
  	  for single in row:
  		  header.append(single)
  	else:
  	  final = {}
  	  for index, item in enumerate(header):
  		   final[item]= row[index]

  	  if len(output) <= 100:
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
    output1 = []
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
              if len(output) <= 100:
              	 	output1.append(final)

    delete = 'false'
    id = 'undefined'
    if es.indices.exists(index="csvresult"):
        res = es.search(index="csvresult", body={"query": {"match": {"filename" : inputfile}}})
        id = res['hits']['hits'][0]['_id'] if (len(res['hits']['hits']) > 0)  else 'undefined'

    if id != 'undefined':
      delete = 'true'

    doc = {
        'filename': inputfile,
        'data': output,
    }
    if delete == 'false':
        es.index(index="csvresult", doc_type='records', body=doc)
    #else:
    #    es.index(index='csvresult',doc_type='records',id=id,body=doc)

    return jsonify({'result' : output1})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
