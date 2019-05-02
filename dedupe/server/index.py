from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
import boto3
import pandas as pd
from fastparquet import write

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

inputfile = 'inputoutputofcsv/example5.csv'

s3 = boto3.resource('s3',aws_access_key_id='AKIAWQGV4HBLW42U7EUL',aws_secret_access_key='riihGrGkiIGHW0kqKSeBsvEW4M7cS3VpzAJMXSOa')
bucket = s3.Bucket(u'pythoncsv')

@app.route('/getcsv', methods=['GET'])
def get_stars():
  output = []
  count = 0;
  header = []
  update = 'false'
  id = 'undefined'

  obj = bucket.Object(key=inputfile)
  response = obj.get()
  lines = response[u'Body'].read().splitlines()
  readCSV = csv.reader(lines)

  for index, row in enumerate(readCSV):
    	if count == 0:
  	  count = 1
  	  for single in row:
  		  header.append(single)
  	else:
  	  final = {}
  	  for index, item in enumerate(header):
  		   final[item]= row[index]

  	  if len(output) <= 499:
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

    print(xyz[0])
    print(xyz[1])

    with open(xyz[0]) as csvfile:
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
              if len(output) <= 499:
              	 	output1.append(final)

    df = pd.read_csv(xyz[0], low_memory=False)
    write('output.parquet', df)

    s3.Object('pythoncsv', 'op.parquet').put(Body=open('output.parquet', 'rb'))

    return jsonify({'result' : output1,'remove_duplicates':xyz[1]})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
