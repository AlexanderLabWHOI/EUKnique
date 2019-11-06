#!/usr/bin/env python
# coding: utf-8

# In[7]:


import os
import io
import re
import csv
import subprocess
import requests
import pandas as pd
import numpy as np
import yaml

list_orgs = ["Heterocapsa triquestra", "Amoebophrya", 
             "Alexandrium fundyense", 
             "Pseudo-nitzschia pungens", "Thalassiosira sp."]
list_orgs_short = ["HT", "AB", "AX", "PN", "TP"]

samples_avail = pd.read_csv("../data/forNCBI_MMETSP.csv")


# In[8]:


print(list_orgs)
configfile = "../config.yaml"
with open(configfile, "r") as configfile:
    config = yaml.load(configfile)
REFERENCEDIR = config["referencedir"]
DATADIR = config["datadir"]
relative_dir = "/vortexfs1/omics/alexander/akrinos/scrna-seqwell-analysis" # ".." if we're running from the scripts or something 


# In[9]:


where_to_look = []
MMETSP_names = []

# Get a list of the MMETSP codes corresponding to organisms we used
for g in list_orgs:
    matching_mmetsp = [a for a,b in enumerate(samples_avail['ORGANISM']) if b == g]
    where_to_look.extend([a for a,b in enumerate(samples_avail['ORGANISM']) if b == g])
    MMETSP_names.append(str(samples_avail['SAMPLE_NAME'][where_to_look[len(where_to_look)-1]])) # we could use list() and add all MMETSP files that match, if we wanted
    
MMETSP_names = ["MMETSP0448","MMETSP0795",'MMETSP0347',"MMETSP1060","MMETSP1071"]
#r2 = requests.get("https://zenodo.org/record/1212585/files/MMETSP0004.trinity_out_2.2.0.Trinity.fasta.renamed.fasta")
#open('tests.fasta', 'wb').write(r2.content)


# In[12]:


# Make a directory for each species of interest and then save the FASTA files from Zenodo corresponding to each given species of interest
files_written = []
for gg in range(0,len(MMETSP_names)):
    #file_names = "https://zenodo.org/record/1212585/files/" + MMETSP_names[gg] + ".trinity_out_2.2.0.Trinity.fasta.renamed.fasta" 
    if type(MMETSP_names[gg]) == list: 
        combined_dir = "/vortexfs1/omics/data/mmetsp/johnson/nt"
        file_names = [os.path.join(combined_dir, p +                                    ".trinity_out_2.2.0.Trinity.fasta.renamed.fasta") for p in MMETSP_names[gg]]
    else:
        file_names = os.path.join(REFERENCEDIR, MMETSP_names[gg] + "_clean.fasta")
    print(file_names)
    species_dir_name = os.path.join(relative_dir, DATADIR) #"../data/" 
    if isinstance(file_names, list):
        print("hello")
        for f in range(0, len(file_names)):
            curr_file = file_names[f]
            to_write = species_dir_name + list_orgs[gg].replace(" ", "") + "_" + MMETSP_names[gg][f] + "_nt.fasta"
            #open(to_write, 'wb').write(curr_file.content)
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
        


# In[5]:


counter = 0
for ff in range(0,len(files_written)):
    f = files_written[ff]
    g = MMETSP_names[ff]
    if isinstance(g, list):
        g = "combined"
    if counter == 0:
        print(f)
    
    print(list_orgs[ff].replace(" ", "-"))
    print(f)
    file_loc = "../data/tgMap_" + list_orgs[ff].replace(" ", "-") + "_" + g + ".tsv"
    print(file_loc)
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
