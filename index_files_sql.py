#!/usr/bin/env python

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 18-May-2015                      #
##############################################

import sys
import hashlib
import time
import logging
import glob
import os
import argparse
import sqlite3

from libs.KafNafParserPy import KafNafParser

logger = logging.getLogger(__file__)   

MAX_NGRAM = 8
SEPARATOR = '\t'    

def get_md5_checksum(filename):
    '''
    Obtains the md5 checksum out of a filename
    '''
    md5_hasher = hashlib.md5()
    fd = open(filename)
    buf = fd.read(65536)
    while len(buf) > 0:
        md5_hasher.update(buf)
        buf = fd.read(65536)
    fd.close()
    return md5_hasher.hexdigest()
    

def check_already_existing(db_con, naf_filename):
    '''
    Checks if the given filename already has been indexed or not
    '''
    existing = True
    checksum = get_md5_checksum(naf_filename)
    my_query = 'SELECT * from documents where hash = "%s";' % checksum
    this_cursor = db_con.cursor()
    results = this_cursor.execute(my_query)
    first_hit = results.fetchone()
    if first_hit is None:
        #The document is not in the database
        logger.info('The document is not in the index and will be indexed')
        existing = False
    else:
        this_id, this_has, this_timestamp = first_hit
        logger.info('The document is already in the index. It was created at %s' % this_timestamp)
        existing = True
        
    return existing, checksum 
  
def extract_data_from_file(db_con, naf_filename,document_id):
    global MAX_NGRAM
    naf_obj = KafNafParser(naf_filename)
    lemma_pos_for_tokenid = {}
    for term in naf_obj.get_terms():
        for tokid in term.get_span().get_span_ids():
            lemma_pos_for_tokenid[tokid] = (term.get_lemma(),term.get_morphofeat().split(' ')[0])
        
    data_token = []     # List of (token,lemma,pos,sentenceid)
    for token in naf_obj.get_tokens():
        value = token.get_text()
        tokid = token.get_id()
        if tokid in lemma_pos_for_tokenid:
            lemma, pos = lemma_pos_for_tokenid[tokid]
            data_token.append((token.get_text(),lemma,pos,token.get_sent()))
    del lemma_pos_for_tokenid
    del naf_obj
    
    #Generating stuff
    cross_sentences = False
    created = 0
    this_cursor = db_con.cursor()
    for n in range(len(data_token)):
        for ngramlen in range(1,MAX_NGRAM+1):
            #Generate ngram of len ngramlen starting in position n
            start = n
            end = start + ngramlen
            if end < len(data_token):
                if cross_sentences or (data_token[start][3] == data_token[end][3]):
                    token_ngram = []
                    lemma_ngram = []
                    pos_ngram = []
                    for this_token in data_token[start:end]:
                        token_ngram.append(this_token[0])
                        lemma_ngram.append(this_token[1]) 
                        pos_ngram.append(this_token[2])
                        
                    #CREATE THE STUFF
                    table_name = 'tbl%dgram' % ngramlen
                    this_cursor.execute("insert into "+table_name+" values (NULL,?,?,?,?)" , (SEPARATOR.join(token_ngram), SEPARATOR.join(lemma_ngram), SEPARATOR.join(pos_ngram),document_id))
                    created += 1
                    if created % 10000 == 0:
                        logger.info('Extracted %d ngrams for %s' % (created, naf_filename))
    return created
                        
            
def index_file(db_con,naf_filename):
    '''
    Adds a new file to the index if it is not already there
    '''
    logger.info('Processing file %s' % naf_filename)
    already_existing, checksum = check_already_existing(db_con, naf_filename)
    
   
    total = 0 
    if not already_existing:
        #Create a new document
        if True:
            my_query = 'INSERT INTO documents VALUES (NULL,"%s",DateTime("now"));' % checksum
            this_cursor = db_con.cursor()
            this_cursor.execute(my_query)
            document_id = this_cursor.lastrowid
            created = extract_data_from_file(db_con, naf_filename,document_id)
            total += created
            logger.info('Ngrams for %s extracted. Total: %d' % (naf_filename,created))
        #except Exception as e:
        #    
        #    logger.info('Something went wrong with document %s and it has not been included in the index %s' % (naf_filename,str(e)))
    db_con.commit()
    return total
        
        
def connect_to_db(database_name):
    db_con = None
    if os.path.exists(database_name):
        logger.info('The database %s already exists' % database_name)
        db_con = sqlite3.connect(database_name)
    else:
        db_con = sqlite3.connect(database_name) #Create a new one
        logger.info('The database "%s" does not exist, it will be created.' % database_name)
        cursor = db_con.cursor()
        ## Create the documents table
        cursor.execute('''CREATE TABLE documents (id INTEGER PRIMARY KEY,
                                                  hash VARCHAR NOT NULL,
                                                  timestamp TIMESTAMP);''')
        ## create the ngrams tables
        for ngram in xrange(1,MAX_NGRAM+1):
            create_table = '''CREATE TABLE tbl%dgram (id INTEGER PRIMARY KEY,
                                                      token VARCHAR NOT NULL,
                                                      lemma VARCHAR NOT NULL,
                                                      pos VARCHAR NOT NULL,
                                                      document INT NOT NULL,
                                                      FOREIGN KEY(document) REFERENCES documents(id));''' % ngram
            cursor.execute(create_table)
        db_con.commit()
    return db_con

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Indexes a set of NAF files into a database', version='1.0')
    parser.add_argument('-db',dest='database_name',help='Name of the database',required=True)
    parser.add_argument('-i', dest='input_folder', help='Input folder with NAF files', required = True)
    
    args = parser.parse_args()
    
    
    #Creating the logger object, re
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    ################################
    
    logger.info('Starting the indexing process')


    # Check if the general database exists or not
    db_con = connect_to_db(args.database_name)
    total = 0 
    for naf_filename in glob.glob(os.path.join(args.input_folder,'*.naf')):
        total_per_file = index_file(db_con, naf_filename)
        total += total_per_file

    
    logger.info('Processed done. Total ngrams: %d' % (total))
    db_con.close()