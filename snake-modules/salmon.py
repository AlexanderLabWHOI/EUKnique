configfile: "config.yaml"

import io
import os
import yaml
import csv
import pandas as pd
import numpy as np
import pathlib
from snakemake.exceptions import print_exception, WorkflowError 

with open("config.yaml", "r") as configfile:
    config = yaml.load(configfile)
    
with open("cluster.yaml", "r") as clusterfile:
    cluster = yaml.load(clusterfile)

INPUTDIR = config["inputdir"]
REFERENCEDIR = config["referencedir"]
SCRATCHDIR = config["scratch"]
OUTDIR = config["outputdir"]
DATADIR = config["datadir"] # for transcriptomes not in MMETSP
SUBDIRECTORY = config["subdirectory"]
SUBDIR_TABLE = pd.read_csv(SUBDIRECTORY, sep = "\t")
DATE = config["date"]

PN_name = config["pn"]
Alex_name = config["alex"]
Parasite_name = config["amoeb"]
Ehux_name = config["ehux"]
Thaps_name = config["thaps"] 
Heterocap_name = config["het"]
DICT_NAMES = {Heterocap_name:"HT",\
              Thaps_name:"TP",\
              PN_name:"PN",\
              Parasite_name:"AB",\
              Alex_name:"AX",\
              Ehux_name:"EH"} 
DICT_CODES = {v: k for k, v in DICT_NAMES.items()} 

GROUP_NAMES = []

# Creates the salmon indices for the groupings of organisms in
# scRNA-seq SeqWell experiment. 
# 
# @param list_species The organisms that we want in the index 
def make_index(list_species, reverse_name=False):
    string_input = ""
    tg_map_names = ""
    
    if reverse_name == False:
        species_sep = list_species.split("_")
        for species in species_sep:
            string_input = string_input + os.path.join(DATADIR, species + "_combined_nt.fasta") + " "
            tg_map_names = tg_map_names + os.path.join(DATADIR, "tgMap_" + species + ".tsv ")
    else:
        string_input = os.path.join(DATADIR, reverse_name + "_combined_nt.fasta")
        tg_map_names = tg_map_names + os.path.join(DATADIR, "tgMap_" + reverse_name + ".tsv")
    
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
    
def make_tg_reverse(short_name):
    file_loc = os.path.join(DATADIR, "tgMap_" + short_name + ".tsv") #list_orgs[ff].replace(" ", "-") + "_" + g + ".tsv"
    os.system("touch " + file_loc)

    with open(file_loc, 'wt') as tgMap_file:
        transcript_to_gene = csv.writer(tgMap_file, delimiter='\t')
        command = str("cat " + os.path.join(DATADIR, str(short_name) + "_combined_nt.fasta") + " | grep \">\" | cut -f2 -d \">\" | cut -f1 -d \" \" > transcript_names.txt")
        os.system(command)
        print(command)
        transcripts = open("transcript_names.txt", "r")
        for transcript in transcripts:
            print(transcript)
            genes = [transcript.replace("\n",""), short_name + "-" + "DN" + transcript.split("_")[1].replace("\n", "")]
            transcript_to_gene.writerow(genes)
    
    #os.system("mv " + os.path.join(DATADIR,"tgMap.tsv ") + file_loc)
    tgMap_file.close()

FILE_NAMES = SUBDIR_TABLE.File
INDEX_NAMES = SUBDIR_TABLE.Index
DIRECTORIES = SUBDIR_TABLE.Directory

list_cultures = INDEX_NAMES
print(list_cultures)

if config["usereverse"] == 0:
    for list_species in list_cultures:
        make_index(list_species)
else:
    # we want to build the index from the reverse reads, assembled via Trinity
    for num_index in range(len(DIRECTORIES)):
        dir_curr = DIRECTORIES[num_index]
        list_species = list_cultures[num_index]
        
        # should return the R1 and R2 files of the sample
        list_files = sorted(os.listdir(os.path.join(INPUTDIR, dir_curr)))
        os.system("Trinity --max_memory " + "150" + "G --seqType fq --single " + os.path.join(INPUTDIR, dir_curr, list_files[1]))
        os.system("mv trinity_out_dir/Trinity.fasta " + os.path.join(DATADIR, dir_curr + "_combined_nt.fasta"))
        os.system("rm -r trinity_out_dir/")
        print("made it to trinity")
        make_tg_reverse(dir_curr)
    
        make_index(list_species,dir_curr) # now we have a Fasta file and tgMap file in the datadir to work off of
