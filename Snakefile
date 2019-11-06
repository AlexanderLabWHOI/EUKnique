configfile: "config.yaml"

import io
import os
import yaml
import pandas as pd
import numpy as np
import pathlib
from snakemake.exceptions import print_exception, WorkflowError 

with open("config.yaml", "r") as configfile:
    config = yaml.load(configfile)

INPUTDIR = config["inputdir"]
REFERENCEDIR = config["referencedir"]
SCRATCHDIR = config["scratch"]
OUTDIR = config["outputdir"]
DATADIR = config["datadir"] # for transcriptomes not in MMETSP
SUBDIRECTORY = config["subdirectory"]
SUBDIR_TABLE = pd.read_csv(SUBDIRECTORY, sep = "\t")
DATE = config["date"]

include: "modules/alevin-snake"

PN_name = config["pn"]
Alex_name = config["alex"]
Ehux_name = config["ehux"]
Thaps_name = config["thaps"]
Heterocap_name = config["het"]
DICT_NAMES = {Heterocap_name:"HT",\
              Thaps_name:"TP",\
              PN_name:"PN",\
              Alex_name:"AX",\
              Ehux_name:"EH"}  
DICT_CODES = invert_dict(DICT_NAMES)

GROUP_NAMES = []

FILE_NAMES = SUBDIR_TABLE.File
INDEX_NAMES = SUBDIR_TABLE.Index
DIRECTORIES = SUBDIR_TABLE.Directory

list_cultures = INDEX_NAMES

rule all:
    input: 
        # Output directory as created via alevin
        # zip or two expand statements
        outputDir = expand(os.path.join(OUTDIR, "{directory}", "{index_name}", "{group_name}"), zip, directory = DIRECTORIES, group_name = FILE_NAMES, index_name = INDEX_NAMES)

