# Dedupe

Table of Contents
-----------------

  - [Front-End](#FrontEnd)
  - [Dedupe-Server](#Server)

FrontEnd
--------
 - **How to Start Front-End**
    - clone project
    - cd Python-ram/dedupe
    - Run `ng serve`,Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

Server
--------
 - **How to Start Server**
    - cd Python-ram/dedupe/server
    - Run `Source venve/bin/activate` and then type `Python index.py` to start dedupe server on `http://localhost:5000/`.

List of API
------------

| No| Name                                           | Description                                                       |
|---|------------------------------------------------| ------------------------------------------------------------------|
| 1.|**serverpath**/getcsv                           | read csv file from server and return 500 records                  |
| 2.|**serverpath**/getquestions                     | return back array of 2 question each time                         |
| 3.|**serverpath**/getnewcsv                        | return back 500 records after process of duplication by dedupe    |

- **Process of api and dedupe**
  - **serverpath**/getcsv
      - When user go to `http://localhost:4200/` this api hit, which read CSV file **`inputoutputofcsv/example5.csv`** from Amazon **s3** bucket named **`'pythoncsv'`**. which contains **2000** records with the help of python **`boto3`** and **`csv`** package
      - From that **2000** records we push **500** records into array to display on frontend side.
      - Return that array with **jsonify**
      
  - **serverpath**/getquestions
      - When user click on `'Remove Duplicates'` button on frontend side, this api hit in server.
      - Here we also read same file from Amazon **s3** bucket with the help of **`boto3`** and **`csv`** packages.
      - Now we clean up records with help of **`unidecode`** and **`column.decode`**, which is help us to remove empty records from our data.
      - After cleaning of records we will store those clean record into variable name **data_d**. In which each readord identify with **`unique_id`**.
      - Next, we will create deduper object by help of **dedupe** package and **dedupe.Dedupe(variables)**. where **`variables`** is set of rules like how each field match with others('shortstring','exact','string'). 
      - when we get both object( **dedupe**, **data_d** ), we call **deduper.uncertainPairs()**. It will give us 2 question pair which is based on our variables declaration.
      - This pair of question array, api return to user.
      
  - **serverpath**/getnewcsv
    - This api will hit, when user click on **Terminate** button on frontend side.
    - Api request contain one json file which have **match** and **dismatch** named array.This file was created on frontend side when user clicked on `Yes` and `No` for every questions asked by upper api.
    - If our **deduper** object was empty then we need to read csv file again and create **deduper** object again.
    - Here we will read our actual file **`inputoutputofcsv/input.csv`** from Amazon **s3** bucket which contain **10 Lakh** records. We processed it and create new **data_d** object.
    - Now we continue to trained our data with **deduper.markPairs(jsonfile)** and **deduper.train()**. This function trained data for our actual **10 Lakh** records.
    - With the help of **deduper.threshold(data_d, recall_weight=2)** we found our threshold value which used in **deduper.match(data_d, threshold)** to found clustered_dupes.
    - **clustered_dupes** contain those records which threshold value match with this threshold value.
    - From clustered_dupes, we create one more array named **cluster_membership** to gave **`cluster id`**,**`canonical representation`**,**`confidence score`**. we got `canonical representation` by **dedupe.canonicalize(cluster_d)**
    - Finally we had duplicate records in array, number of duplicates records. We merged with our **10 Lakhs** records serialize and store into csv file.
    - Here we read this new output csv by `pandas` pacakage with `pd.read_csv('filename', low_memory=False)` to create **parquat** data and save it on Amazon **s3** bucket with `write('output.parquet', 'paquatdata')`
    - For user, we read 500 records from output csv file and return that array as response of api.
    - This api takes min 15-20 min to complete. 
    
