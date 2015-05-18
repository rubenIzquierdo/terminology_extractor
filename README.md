#Terminology extractor with patterns#

This repository contains a set of scripts and tools to extract relevant terms or multiterms from a corpus of documents given a set of patterns. Specifically it allows to
automatically:

* Process the documents through a shallow pipeline in order to obtain morphological tags and lemma information for every token
* Index the processed documents into a SQL database which will be queried by the pattern extractor.
* Extract relevant terms or multiterms from the database given a set of patterns


##Installation##

All the scripts are developed in Python, and using standard libraries so the external dependencies. The only external
reference is to one wrapper for the TreeTagger pos-tagger and lemmatizer (https://github.com/rubenIzquierdo/treetagger_plain2naf),
and one library (https://github.com/cltl/KafNafParserPy.git) to parse KAF/NAF files (the format used to store the processed files).
The `install.sh` will take care of installing all the requirements automatically, so you only need to clone this repository and run this
script.
```shell
git clone https://github.com/rubenIzquierdo/terminology_extractor.git
cd terminology_extractor
. install.sh
```

##Step 1: processing your plain text files##

The first step is to process through the pipeline all the files that compose your corpus. All these files are considered to be
UTF-8 plain text files. The easiest way to process all of them is to create a folder and copy all the files within that folder.
Once this is done, we can use the script `convert_to_naf.sh`, which will read all the files in the input folder and it will
process every file through the pipeline. The resulting files will be stored with NAF format in the output folder. Both input
and output folders are parameters to the script. Example:
```shell
. convert_to_naf.sh in_folder out_folder
```


##Step 2: create a database of ngrams from KAF/NAF##

Once the files have been processed, and are available as NAF files containing token, part-of-speech and lemma information, the database
can be created. The database selected is sqlite, as it is integrated with Python, it is easy to use and it does not require any installation.
In order to create a database of ngrams from a list of KAF or NAF files, you should use the script `index_files_sql.py`. Modify
the parameter `MAX_NGRAM` hard coded in this file to select the maximum length of your ngrams (default is 8). You can get the
description of parameters by calling `index_files_sql.py -h`:
```shell
usage: index_files_sql.py [-h] [-v] -db DATABASE_NAME -i INPUT_FOLDER

Indexes a set of NAF files into a database

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -db DATABASE_NAME  Name of the database
  -i INPUT_FOLDER    Input folder with NAF files
```

The two required parameters are the name of the database (`-db`), which will be created if it does not exist, and the input folder (`-i`)
with the list of KAF/NAF files. The database will consist of one table which stores the documents (and checksums to avoid duplicates), and
one table for every ngram size (one for unigram, one for bigram...), which stores the token, lemma and pos ngrams. One example:
```shell
python index_files_sql.py -i folder_naf_files -db my_database_file.sql
```

The database needs to be created just once, unless you have new documents that you would like to incorporate. In this case you can run
the same script but only for the new documents (in fact if you try to index twice the same document, with exactly the same content, the
script will detect it and it will ignore the second trial to index the document.)

##Step 3: extracting terms from patterns##

The final and most interesting step is to extract relevant pieces of information from your database providing a set of patterns. You
can query the database created in the previous step with the script `extract_patterns.py`, in order to extract pieces of text that fit
a list of patterns provided. The patterns need to be stored in one XML file, with this specific schema:
```xml
<patterns>
  <pattern len="4">
    <p key="token" position="0" values="training"/>
    <p key="token" position="1" values="method methods"/>
    <p key="token" position="2" values="in on for to using"/>
    <p key="pos" position="3" values="nn"/>
  </pattern>
</patterns>
```

You have to provide for every pattern the list of restrictions for that pattern (elements <p>), with consists of a key (token, lemma or pos), the position
(considering 0 to be the first one), and the list of possible values (separated by whitespaces). So for instance the previous pattern would retrieve:

* All the 4-grams (a sequence of 4 terms)
* With the token `training` as the first element (position 0)
* With the token `method` or `methods` as the second element (position 1)
* With one of the token in the list "in/on/for/to/using" as third element (position 2)
* And with a noun (pos tag is nn) as the 4th element

So, *"training methods in agriculture"* or *"training method for coffee"* would be two 4-grams that match our defined pattern. The file `training_course_patterns.xml` included in this repository
contains some example patterns.

If you run `extract_patterns.py -h` you will get the help of the program.

```shell
usage: extract_patterns.py [-h] [-v] -db DATABASE_NAME -p PATTERNS_FILE

Extracts ngrams matching a list of patterns

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -db DATABASE_NAME  Name of the database
  -p PATTERNS_FILE   XML file with the input patterns
```

The two parameteres are the database created in the previous step, and the XML file with the patterns. You will get in the output a list of matching texts, 
together with the global frequency in your database.


##Contact##
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
* http://rubenizquierdobevia.com/

