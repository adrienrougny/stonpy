#!/bin/bash
DIR=`dirname $0`
java -cp ${DIR}/cd2sbgnml-0.4.5-app.jar fr.curie.cd2sbgnml.Cd2SbgnmlScript -i $1 -o $2
