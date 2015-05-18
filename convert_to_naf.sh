#!/bin/bash

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 18-May-2015                      #
##############################################


if [ $# -ne 2 ];
then
  echo "Usage: $0 input_files naf_output"
  echo "Where:"
  echo "        input_files: path to folder with plain files"
  echo "        naf_output:  path to folder to store the NAF files (will be removed if it exists!!!)"
  echo
  exit -1
fi 

here=$(pwd)
input_folder=$1
output_folder=$2

if [ -d $output_folder ];
then
  echo "Output folder already exist, moved to $output_folder.bu"
  mv $output_folder $output_folder.bu
fi

mkdir $output_folder


path_to_tagger="python $here/libs/treetagger_plain2naf/treetagger_plain2naf.py -l en"

for ifile in $input_folder/*
do
  echo "Processing $ifile"
  basefile=$(basename $ifile)
  ofile=$output_folder/$basefile.naf
  efile=$ofile.err
  cat $ifile | $path_to_tagger > $ofile 2> $efile
  echo "  Done, " $(wc -l $ofile)
done
