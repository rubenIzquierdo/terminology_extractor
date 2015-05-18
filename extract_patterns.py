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

from collections import defaultdict 
import xml.etree.cElementTree as etree 
import sys
import sqlite3
import argparse


def get_all_ngrans(db_con, this_len):
    
    table_name = 'tbl%dgram' % this_len
    
    my_cursor = db_con.cursor()
    for hit in my_cursor.execute('select * from '+table_name):
        #hit -> (21809, u'g.\tfruit\t,', u'g.\tfruit\t,', u'FW\tNN\t,', 1)
        json_obj = {'tokens': hit[1].lower().split('\t'),
                    'lemmas': hit[2].lower().split('\t'),
                    'pos': hit[3].lower().split('\t'),
                    }
        yield json_obj

        
def get_hits(db_con, this_len,set_of_patterns):
    selected = []
    for json_obj in get_all_ngrans(db_con, this_len):
        for pattern in set_of_patterns:
            selected_according_to_this_pattern = True
            for piece_of_pattern in pattern:
                key, position, values = piece_of_pattern
                #FOR pos we use only the first character
                if key == 'pos':
                    this_value = json_obj[key][position][0]
                    possible_values = [v[0] for v in values]
                else:
                    this_value = json_obj[key][position]
                    possible_values = values
                    
                if not this_value in possible_values:
                    selected_according_to_this_pattern = False
                    break
            if selected_according_to_this_pattern:
                selected.append(json_obj)
                break   #has been already selected            
    return selected


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Extracts ngrams matching a list of patterns", version="1.0")
    parser.add_argument('-db',dest='database_name',help='Name of the database',required=True)
    parser.add_argument('-p', dest='patterns_file', help='XML file with the input patterns', required=True)
    
    args = parser.parse_args()
    
    
    
    agglomerated = defaultdict(int)
    db_con = sqlite3.connect(args.database_name)
    
    patterns = {}
    my_obj = etree.parse(args.patterns_file)
    for pattern_node in my_obj.findall('pattern'):
        this_len = pattern_node.get('len')
        ignore_this =(pattern_node.get('ignore',"0") == "1")
        if not ignore_this:
            if this_len not in patterns:
                patterns[this_len] = []
            this_pattern = []
            for p in pattern_node:
                piece_of_pattern = (p.get('key'), int(p.get('position')), p.get('values').split(' '))
                this_pattern.append(piece_of_pattern)
            patterns[this_len].append(this_pattern)
            
    for this_str_len, these_patterns in patterns.items():
        for json_obj in get_hits(db_con, int(this_str_len), these_patterns):
            agglomerated[' '.join(json_obj['tokens'])] += 1


    ######################
    # PRINTING THE RESULTS
    #######################
    for value, count in sorted(agglomerated.items(),key=lambda t: -t[1]):
        print count, value.encode('utf-8')
    
    sys.exit(0)
    
        
        
        
        
        
        
        
        