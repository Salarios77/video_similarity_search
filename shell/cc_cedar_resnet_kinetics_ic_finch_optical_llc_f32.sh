#!/bin/bash
#SBATCH --account=def-florian7_gpu 
#SBATCH --time=7-00:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=kin_ic_finch_llc_optical_f32
#SBATCH --output=%x-%j.out
#SBATCH --gres=gpu:p100l:4
#SBATCH --mem=100G
#SBATCH --cpus-per-task=24
# --wait-all-nodes=1


module load python/3.6
source /home/cheny257/projects/def-florian7/cheny257/code/resnet_env/bin/activate


clush -w $(slurm_hl2hl.py --format PDSH) tar -xzf /home/cheny257/projects/def-florian7/datasets/kinetics400/frames_shortedge320px_25fps/val_split.tar.gz -C $SLURM_TMPDIR
echo 'Extracted val zip'
clush -w $(slurm_hl2hl.py --format PDSH) tar -xzf /home/cheny257/projects/def-florian7/datasets/kinetics400/frames_shortedge320px_25fps/train_split.tar.gz -C $SLURM_TMPDIR
echo 'Extracted train zip'

#flow
clush -w $(slurm_hl2hl.py --format PDSH) tar -xzf /home/cheny257/projects/def-florian7/datasets/kinetics400/FLOW/FLOW-u-jpg.tar.gz -C $SLURM_TMPDIR
echo 'Extracted flow train zip'

cd $SLURM_TMPDIR

export MASTER_ADDRESS=$(hostname)
echo $MASTER_ADDRESS

MPORT=3456
echo $MPORT

ROOTDIR=/home/cheny257/projects/def-florian7/cheny257/code/video_similarity_search


srun python $ROOTDIR/online_train.py \
--cfg $ROOTDIR/code/config/custom_configs/cc_resnet_kinetics_itercluster_optical_llc_f32.yaml \
--gpu 0,1,2,3 \
--num_data_workers 4 \
--batch_size 32 \
--output '/home/cheny257/projects/def-florian7/cheny257/output/kin_ic_finch_llc_no_optical_f32' \
--epoch 601 \
--num_shards 2 \
--ip_address_port tcp://$MASTER_ADDRESS:$MPORT \
--compute_canada \
--iterative_cluster VAL.BATCH_SIZE 32
