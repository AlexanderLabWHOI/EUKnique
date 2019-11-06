import os
import sys
import yaml
import numpy as np 
import pandas as pd

with open("config.yaml", "r") as configfile:
    config = yaml.load(configfile)

INPUTDIR = config["inputdir"]
SUBDIRECTDIR = config["subdirectory"]

# We want to get the location of all the files we're interested in using.
sampledirs = os.listdir(INPUTDIR)

subdirectory_table = pd.DataFrame({'Directory': [], \
                                   'File': [], \
                                   'Index': []})

for s in sampledirs:
    files = list(set([p.split("_R")[0] for p in os.listdir(os.path.join(INPUTDIR, s))]))
    indices = [p.split("_S")[0] for p in files]
    indices = ["".join(i for i in index if not i.isdigit()) for index in indices]
    indices = [index.split("_") for index in indices]
    if "AX3" in files[0].split("_"):
        indices[0].append("AB") 
    indices = ["_".join(sorted(list(set([i for i in index if i])))) for index in indices]
    thisset = pd.DataFrame({'Directory': [s] * len(files), \
                            'File': files, \
                            'Index': indices})
    subdirectory_table = subdirectory_table.append(thisset)

print(subdirectory_table)
subdirectory_table.to_csv(path_or_buf = SUBDIRECTDIR, sep = "\t")
