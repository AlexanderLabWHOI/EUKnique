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

PN_name = config["pn"]
#Alex_name = "Alexandrium-catenella_MMETSP0790"
#Alex_name = "Alexandrium_combined"
Alex_name = config["alex"]
Parasite_name = config["amoeb"]
Ehux_name = config["ehux"]
Thaps_name = config["thaps"] # Thalassiosira-sp._MMETSP1071
Heterocap_name = config["het"]
DICT_NAMES = {Heterocap_name:"HT",\
              Thaps_name:"TP",\
              PN_name:"PN",\
              Parasite_name:"AB",\
              Alex_name:"AX",\
              Ehux_name:"EH"} 
DICT_CODES = invert_dict(DICT_NAMES) 

GROUP_NAMES = []

# Creates the salmon indices for the groupings of organisms in
# scRNA-seq SeqWell experiment. 
# 
# @param list_species The organisms that we want in the index 
def make_index(list_species):
    string_input = ""
    tg_map_names = ""
    species_sep = list_species.split("_")
    for species in species_sep:
        t = DICT_CODES[species]
        string_input = string_input + os.path.join(REFERENCEDIR, t.split("_")[1] + "_clean.fasta") + " "             
        #string_input = string_input + " " + os.path.join(DATADIR, t + "_nt.fasta")
        tg_map_names = tg_map_names + os.path.join(DATADIR, "tgMap_" + t + ".tsv ")
    
    print(string_input)
    path_fasta = os.path.join(DATADIR, list_species + ".fa")
    path_tgmap = os.path.join(DATADIR, "tgMap_" + list_species + ".tsv")
    
    # concatenate FASTA files
    os.system("cat " + string_input + " > " + path_fasta)
    
    # create salmon index 
    os.system("salmon index -t " + path_fasta + " -i data/indices/" + list_species + "_index -k 31")        
    salmon_index = os.path.join(DATADIR, "indices", list_species + "_index")    

    # concatenate transcript-to-gene maps
    os.system("cat " + tg_map_names + " > " + path_tgmap)


list_cultures = [[Ehux_name], [Alex_name,Parasite_name],[Alex_name,Heterocap_name],[Thaps_name],[Alex_name,Heterocap_name],[Alex_name,PN_name],[Alex_name],[PN_name,Thaps_name,Alex_name,Heterocap_name],[PN_name]] 

FILE_NAMES = SUBDIR_TABLE.File
INDEX_NAMES = SUBDIR_TABLE.Index
DIRECTORIES = SUBDIR_TABLE.Directory

list_cultures = INDEX_NAMES
print(list_cultures)

for list_species in list_cultures:
    make_index(list_species)
