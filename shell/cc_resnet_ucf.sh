#!/bin/bash
#SBATCH --account=def-florian7_gpu
#SBATCH --time=1-18:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=6
#SBATCH --gres=gpu:t4:4
#SBATCH --mem=48G
#SBATCH --job-name=resnet_ucf
#SBATCH --output=%x-%j.out

cd $SLURM_TMPDIR
mkdir work_ucf
cd work_ucf
tar -xzf /home/cheny257/projects/def-florian7/datasets/UCF101/jpg.tar.gz
echo 'Extracted jpg.tar.gz'

python /home/cheny257/projects/def-florian7/cheny257/code/video_similarity_search/train.py \
--cfg '/home/cheny257/projects/def-florian7/cheny257/code/video_similarity_search/config/custom_configs/cc_resnet_ucf.yaml' \
--output '/home/cheny257/projects/def-florian7/cheny257/output/ResNet18_U' \
--checkpoint_path 'checkpoint:/home/cheny257/projects/def-florian7/cheny257/output/ResNet18_U/tnet_checkpoints/3dresnet/checkpoint.pth.tar' \
--gpu 0,1,2,3 \
--batch_size 40 \
--num_data_workers 4 \
--epoch 200