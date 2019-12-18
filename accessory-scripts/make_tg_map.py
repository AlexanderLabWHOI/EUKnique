#!/usr/bin/env python
# coding: utf-8

import os
import io
import re
import csv
import subprocess
import requests
import pandas as pd
import numpy as np
import yaml

samples_avail = pd.read_csv("../data/forNCBI_MMETSP.csv")
sample_names = samples_avail.SAMPLE_NAME
configfile = "../config.yaml"
with open(configfile, "r") as configfile:
    config = yaml.load(configfile)
    
REFERENCEDIR = config["referencedir"]
DATADIR = config["datadir"]
relative_dir = "/vortexfs1/omics/alexander/akrinos/scrna-seqwell-analysis" # ".." if we're running from the scripts or something 

org_list = config["configlist"].split(",")
short_names = config["smallnamelist"].split(",")
list_orgs_short = []
MMETSP_names = []
list_orgs = []
for curr_num in range(len(org_list)):
    curr = org_list[curr_num]
    MMname_list = config[curr].split(",")
    MMname_curr = []
    orgnames_curr = []
    for mm in MMname_list:
        MMname_curr.append(mm.split("_")[1])
        orgnames_curr.append(mm.split("_")[0])
        list_orgs_short.append(short_names[curr_num]) # add multiple copies of the short name if we have multiple transcriptomes
    MMETSP_names.extend(MMname_curr)
    list_orgs.extend(orgnames_curr)
print(MMETSP_names)

# Make a directory for each species of interest and then save the FASTA files from Zenodo corresponding to each given species of interest
files_written = []
for gg in range(0,len(MMETSP_names)):
    # if the current sample is not in the MMETSP list
    if MMETSP_names[gg] not in sample_names:
        file_names = "Acatassembly.fasta"
    else:
        file_names = os.path.join(REFERENCEDIR, MMETSP_names[gg] + "_clean.fasta")
        
    print(file_names)
    species_dir_name = os.path.join(relative_dir, DATADIR) 
    if isinstance(file_names, list):
        for f in range(0, len(file_names)):
            curr_file = file_names[f]
            to_write = species_dir_name + list_orgs[gg].replace(" ", "") + "_" + MMETSP_names[gg][f] + "_nt.fasta"
            os.system("cp " + curr_file + " " + to_write)
            
        print(" ".join(file_names))
        os.system("cat " + " ".join(file_names) + " > " +                   os.path.join(relative_dir, DATADIR, list_orgs[gg].replace(" ", "") + "_" + "combined" + "_nt.fasta"))
        to_write = os.path.join(relative_dir, DATADIR, list_orgs[gg].replace(" ", "") + "_" + "combined" + "_nt.fasta")
    else:
        curr_file = file_names
        to_write = species_dir_name + list_orgs[gg].replace(" ", "-") + "_" + MMETSP_names[gg] + "_nt.fasta"
        #open(to_write, 'wb').write(curr_file.content)
        os.system("cp -f " + curr_file + " " + to_write)
    files_written.append(to_write) # need to extend if using list option
        
counter = 0
for ff in range(0,len(files_written)):
    f = files_written[ff]
    g = MMETSP_names[ff]
    if isinstance(g, list):
        g = "combined"
    if counter == 0:
        print(f)
    
    file_loc = "../data/tgMap_" + list_orgs[ff].replace(" ", "-") + "_" + g + ".tsv"
    os.system("touch " + file_loc)

    with open("../data/tgMap.tsv", 'wt') as tgMap_file:
        transcript_to_gene = csv.writer(tgMap_file, delimiter='\t')
        if g == "combined":
            command = str("cat " + str(f) + " | grep \">\" | cut -f2 -d \">\" | cut -f1 -d \" \" > transcript_names.txt")
        else:
            command = str("cat " + str(f) + " | grep \">\" | cut -f2 -d \">\" > transcript_names.txt")
        os.system(command)
        transcripts = open("transcript_names.txt", "r")
        for transcript in transcripts:
            #print(transcript)
            if g == "combined":
                genes = [transcript.replace("\n",""), list_orgs_short[ff] + "-" + transcript.split("TRINITY_")[1].split("_")[0]]
            else:
                genes = [transcript.replace("\n",""), list_orgs_short[ff] + "-" + "DN" + transcript.split("|")[3].replace("\n", "")]
            counter = counter + 1
            transcript_to_gene.writerow(genes)
    
    os.system("mv ../data/tgMap.tsv " + file_loc)
    tgMap_file.close()

print("Done!")
