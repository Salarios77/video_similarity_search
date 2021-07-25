#!/bin/bash
#SBATCH --account=def-florian7_gpu
#SBATCH --time=3-20:10:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=finch_resnet_ucf_ic_llc_optical_pos_replace_1.0
#SBATCH --output=%x-%j.out
#SBATCH --gres=gpu:v100l:2
#SBATCH --mem=40G
#SBATCH --cpus-per-task=16
# --wait-all-nodes=1

module load python/3.6

source /home/cheny257/projects/def-florian7/cheny257/code/resnet_env/bin/activate


clush -w $(slurm_hl2hl.py --format PDSH) tar -xf /home/cheny257/projects/def-florian7/datasets/UCF101/jpg.tar.gz -C $SLURM_TMPDIR
echo 'Extracted jpg.tar.gz'

clush -w $(slurm_hl2hl.py --format PDSH) tar -xf /home/cheny257/projects/def-florian7/datasets/UCF101/ucf101_tvl1_flow-2.tar.gz -C $SLURM_TMPDIR
echo 'Extracted ucf101_tvl1_flow-2.tar.gz'

cd $SLURM_TMPDIR


# export MASTER_ADDRESS=$(hostname)
# echo master_address:$MASTER_ADDRESS

# MPORT=3463
# echo master_port:$MPORT

srun python /home/cheny257/projects/def-florian7/cheny257/code/video_similarity_search/online_train.py \
--cfg '/home/cheny257/projects/def-florian7/cheny257/code/video_similarity_search/config/custom_configs/ablation/finch/cc_resnet_ucf_ic_llc_optical_pos_replace1.0.yaml' \
--gpu 0,1 \
--num_data_workers 4 \
--batch_size 32 \
--checkpoint_path '/home/cheny257/projects/def-florian7/cheny257/output/ablation/finch/resnet_ucf_ic_llc_optical_pos_replace_1.0/tnet_checkpoints/3dresnet/checkpoint.pth.tar' \
--output '/home/cheny257/projects/def-florian7/cheny257/output/ablation/finch/resnet_ucf_ic_llc_optical_pos_replace_1.0' \
--epoch 601 \
--compute_canada \
--iterative_cluster \