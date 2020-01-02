import os
import sys
import yaml
import numpy as np 
import pandas as pd
import io
import re
import csv
import subprocess
import requests
from snakemake.exceptions import print_exception, WorkflowError

relative_dir = "/vortexfs1/omics/alexander/akrinos/euknique" # ".." if we're running from the scripts or something 
with open(relative_dir + "/config.yaml", "r") as configfile:
    config = yaml.load(configfile)
    
relative_dir = config["homedir"]
    
INPUTDIR = config["inputdir"]
SUBDIRECT = config["subdirectory"]
REFERENCEDIR = config["referencedir"]
DATADIR = config["datadir"]

samples_avail = pd.read_csv(os.path.join(DATADIR, "forNCBI_MMETSP.csv"))
sample_names = list(samples_avail.SAMPLE_NAME)
sample_names = [curr.split("C")[0].split("_")[0] for curr in sample_names]
    
##### CREATE SUBDIRECTORY TABLE #####

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
    
    # this is only if you have the S000X in the file name
    indices = [[i for i in indices_short if i != 'S'] for indices_short in indices]   

    # AX3 indicates that we have an infected form of amoebaphyra
    if "AX3" in files[0].split("_"):
        indices[0].append("AB") 
    indices = ["_".join(sorted(list(set([i for i in index if i])))) for index in indices]
    thisset = pd.DataFrame({'Directory': [s] * len(files), \
                            'File': files, \
                            'Index': indices})
    subdirectory_table = subdirectory_table.append(thisset)

print(subdirectory_table)
subdirectory_table.to_csv(path_or_buf = os.path.join(relative_dir,SUBDIRECT), sep = "\t")


# The org_list is the name of all the organisms we want to get references for
# This list has other entries in the configfile corresponding to the 
# reference we wish to use for that organism 
org_list = config["configlist"].split(",")
# The short_names list is the two-letter codes of these organisms
short_names = config["smallnamelist"].split(",")

##### CREATE LIST FOR EACH OF THE SET OF TRANSCRIPTOMES WE'RE USING #####

# Now we'll build a list of repeated entries based on how many references
# we're using for each organism and where they are
list_orgs_short = []
MMETSP_names = []
list_orgs = []
for curr_num in range(len(org_list)):
    curr = org_list[curr_num]
    MMname_list = config[curr].split(",")
    MMname_curr = []
    orgnames_curr = []
    for mm in MMname_list:
        print(mm)
        MMname_curr.append(mm.split("_")[1])
        orgnames_curr.append(mm.split("_")[0])
        
    list_orgs_short.append(short_names[curr_num])
    MMETSP_names.append(MMname_curr) # we want to add a list of entries if we have multiple transcriptomes/species
    list_orgs.append(orgnames_curr)
print(MMETSP_names)

##### Copy over a combined version of each set of FASTA files #####

# Make a directory for each species of interest and then save the FASTA files 
files_written = []
for gg in range(0,len(MMETSP_names)):
    file_names = []
    for f in MMETSP_names[gg]:
        # if the current sample is not in the MMETSP list
        if f not in sample_names:
            # if not in the MMETSP, copy the fasta file to the data directory and name it by exactly 
            # that name in the config file
            file_names.append(os.path.join(DATADIR, f + ".fasta")) #"Acatassembly.fasta")
        else:
            file_names.append(os.path.join(REFERENCEDIR, f + "_clean.fasta"))
        
    species_dir_name = os.path.join(relative_dir, DATADIR) 
    #for f in range(0, len(file_names)):
    #    curr_file = file_names[f]
    #    to_write = species_dir_name + list_orgs[gg][f].replace(" ", "") + "_" + MMETSP_names[gg][f] + "_nt.fasta"
    #    os.system("cp " + curr_file + " " + to_write)

    os.system("cat " + " ".join(file_names) + " > " + os.path.join(species_dir_name, list_orgs_short[gg].replace(" ", "") + "_" + "combined" + "_nt.fasta"))
    to_write = os.path.join(species_dir_name, list_orgs_short[gg].replace(" ", "") + "_" + "combined" + "_nt.fasta")
    files_written.append(to_write) # need to extend if using list option
    
##### CREATE TRANSCRIPT-TO-GENE MAP #####

# Iterate through the combined files of transcriptomes we just wrote
counter = 0
for ff in range(0,len(files_written)):
    f = files_written[ff]
    g = MMETSP_names[ff]
    short_name = list_orgs_short[ff]
    
    file_loc = os.path.join(relative_dir,DATADIR, "tgMap_" + short_name + ".tsv") #list_orgs[ff].replace(" ", "-") + "_" + g + ".tsv"
    os.system("touch " + file_loc)
    os.system("touch " + os.path.join(relative_dir,DATADIR,"tgMap.tsv"))

    #with open(os.path.join(relative_dir,DATADIR,"tgMap.tsv"), 'wt') as tgMap_file:
    with open(file_loc, 'wt') as tgMap_file: 
        transcript_to_gene = csv.writer(tgMap_file, delimiter='\t')
        command = str("cat " + str(f) + " | grep \">\" | cut -f2 -d \">\" | cut -f1 -d \" \" > transcript_names.txt")
        os.system(command)
        transcripts = open("transcript_names.txt", "r")
        for transcript in transcripts:
            #genes = [transcript.replace("\n",""), list_orgs_short[ff] + "-" + "DN" + transcript.split("|")[3].replace("\n", "")]
            if transcript.split("_")[0] == "TRINITY":
                genes = [transcript.replace("\n",""),list_orgs_short[ff]+"-"+transcript.split("_")[1]]
            else:
                if(len(transcript.split("|")) != 4):
                    print(transcript)
                genes = [transcript.replace("\n",""),list_orgs_short[ff]+"-"+"DN"+transcript.split("|")[len(transcript.split("|"))-1].replace("\n","")]
            counter = counter + 1
            transcript_to_gene.writerow(genes)
        #os.system("mv " + os.path.join(relative_dir,DATADIR,"tgMap.tsv ") + file_loc)
    tgMap_file.close()

print("Done!")
