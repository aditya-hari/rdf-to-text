#!/bin/bash
#SBATCH -c 19
#SBATCH --gres gpu:2
#SBATCH -w gnode067
#SBATCH --mem-per-cpu 2G
#SBATCH -A irel
#SBATCH --time 3-00:00:00
#SBATCH --output syn.log
#SBATCH --mail-user aditya.hari@research.iiit.ac.in
#SBATCH --mail-type ALL
#SBATCH --job-name syn

python syntactic_scores.py