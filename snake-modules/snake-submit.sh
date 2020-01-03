#!/bin/bash
#SBATCH --partition=compute

snakemake -s snake-modules/Snakefile --jobs 10 --rerun-incomplete --use-conda --cluster-config snake-modules/cluster.yaml --cluster "sbatch --parsable --qos=unlim --partition={cluster.queue} --job-name=indexcreation.{rule}.{wildcards} --mem={cluster.mem}gb --time={cluster.time} --ntasks={cluster.threads} --nodes={cluster.nodes}"

