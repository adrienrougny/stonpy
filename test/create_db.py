#!python
import os

import stonpy

from credentials import URI, USER, PASSWORD

ston = stonpy.ston.STON(URI, USER, PASSWORD)
ston.graph.delete_all()

DIR = "maps/"
for fname in os.listdir(DIR):
    # if fname.startswith("epi"):
    print("Storing {}...".format(fname))
    sbgnfile = os.path.join(DIR, fname)
    ston.create_map(sbgnfile, fname)
