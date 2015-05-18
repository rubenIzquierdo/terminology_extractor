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

here=$(pwd)
rm -rf libs 2> /dev/null
mkdir libs

#######################
# 0) KafNafParserPy
######################
cd libs
git clone https://github.com/cltl/KafNafParserPy.git


#########################
# 1) Treetagger_plain2naf
#########################
git clone https://github.com/rubenIzquierdo/treetagger_plain2naf
cd treetagger_plain2naf
. install_dependencies.sh
cd ..	# back to libs
##########################

