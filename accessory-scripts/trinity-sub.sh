#!/bin/bash
#SBATCH --partition=compute  
#SBATCH --mem=99999
#SBATCH --time=99999
#SBATCH -N 4
#SBATCH --qos=unlim
#SBATCH -n 16

python snake-modules/preprocessing.py
python snake-modules/salmon-with-snake.py
