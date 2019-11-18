The purpose of this repository is to analyze single-cell RNA sequencing data of eukaryotic algae generated via a Seq-Well experiment. 

## Set-up

To use this repository, the config file needs to updated with the paths of the single-cell RNA-seq data in `fastq` format. In addition, `salmon index` must be used to create a salmon index of the relevant reference genomes and transcriptomes of the species in question for the particular sequence experiment. In order to do this, change the `config.yaml` file to reflect the data input directory, which should be organized via subdirectories of arrays containing the forward and reverse sequence output fasta files. Then, run the following scripts, in this order: 

* `accessory-scripts/make_subdirectory_table.py`
* `accessory-scripts/make_tg_map.py`
* `accessory-scripts/make_salmon_indices.py`

If one of the species being used in one of the arrays is not in the standard list of organisms (_Alexandrium fundyense_, _Heterocapsa rotundata_, _Thalassiosira pseudonana_, and _Pseudo-nitzschia pungens_), a reference transcriptome for the organism following the given naming convention must either be added, or the MMETSP id for that organism must be added such that the reference transcriptome can be retrieved from the MMETSP database.

## Running the pipeline

Running the pipeline is as simple as customizing the script used to generate the salmon index file based on the relevant reference genomes, and then running:

``
snakemake --use-conda
``

in the main directory of the repository. 

## Description of original Seq-Well experiment for which analysis pipeline was designed

This pipeline was originally created for the Seq-Well experiment conducted at WHOI on 7/11-7/12/2019. This consisted of the following successful arrays with corresponding species composition:

* 1 - *Alexandrium sp.*, late infection 
* 2 - *Alexandrium sp.*, 15 deg C normal light-dark (NLD) 
* 3 - *Thalassiosira pseudonana*, 19 deg C NLD & 15 deg C reverse light-dark (RLD) 
* 4 - *Heterocapsa sp.* & *Alexandrium sp.* (check) 
* 5 - *Alexandrium sp.* 10 deg C RLD & *Pseudo-nitzchia sp.* Si-limited 
* 6 - *Alexandrium sp.*, late infection (?, what happened w this?) 
* 7 - *Pseudo-nitzchia sp.*, NLD 15 deg C N-limited & *Thalassiosira pseudonana*, N-limited & *Alexandrium sp.*, 15 deg C NLD & *Heterocapsa sp.*, 15 deg C NLD 
* 8 - *Pseudo-nitzchia sp.*, NLD 15 deg C N-limited & *Pseudo-nitzchia*, N-replete

## Reference transcriptomes ##

For each of the experimental pairings from the experiment, a salmon index file must be created from the reference transcriptomes for each group of organisms. Currently, in order to combine transcriptomes for the purposes of creating the index file, we just concatenate the `fasta` files containing the relevant reference transcriptomes. 

Example listing of data entries used: 

---------------------
| Accession number | Species | URL | ID |
| ---------------  | ------- | --- | -- |
| CAM\_ASM\_000047 | *Heterocapsa rotundata* | https://www.imicrobe.us/#/samples/1663 | MMETSP0503 |
| CAM\_SMPL\_002340 | *Skeletonema costatum* 1716 | https://www.imicrobe.us/#/samples/1676 | MMETSP0013 |
| CAM\_SMPL\_002341 | *Nitzchia sp.* RCC80 | https://www.imicrobe.us/#/samples/1677 | MMETSP0014 |
