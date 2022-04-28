#!/bin/python
import os

import stonpy

from credentials import URI, USER, PASSWORD

ston = stonpy.ston.STON(URI, USER, PASSWORD)

DIR = "maps"
OUTDIR = "maps_from_db"
for fname in os.listdir(DIR):
    print("Retrieving {}...".format(fname))
    sbgn_file = os.path.join(OUTDIR, fname)
    ston.get_map_to_sbgn_file(map_id=fname, sbgn_file=sbgn_file)
