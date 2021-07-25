#!/bin/bash
#SBATCH --account=def-florian7_gpu 
#SBATCH --time=0-00:30:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --gres=gpu:v100l:4
#SBATCH --mem=48G
#SBATCH --job-name=slowfast_ucf
#SBATCH --output=%x-%j.out

cd $SLURM_TMPDIR
mkdir work_ucf
cd work_ucf
tar -xzf /home/salar77h/projects/def-florian7/datasets/UCF101/jpg.tar.gz
echo 'Extracted jpg.tar.gz'

python /home/salar77h/projects/def-florian7/salar77h/repos/video_similarity_search/train.py --cfg /home/salar77h/projects/def-florian7/salar77h/repos/video_similarity_search/config/custom_configs/slowfast_ucf_cc.yaml --gpu 0,1,2,3 --num_data_workers 4 --batch_size 40 --output /home/salar77h/projects/def-florian7/salar77h/repos/video_similarity_search/output_ucf3-new_temporal-64 DATA.SAMPLE_DURATION 64