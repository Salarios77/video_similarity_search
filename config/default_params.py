"""Configs."""
from fvcore.common.config import CfgNode

# Config definition
_C = CfgNode()


# -----------------------------------------------------------------------------
# Training options
# -----------------------------------------------------------------------------
_C.TRAIN = CfgNode()
_C.TRAIN.EPOCHS = 200
_C.TRAIN.BATCH_SIZE = 16
#_C.TRAIN.DATASET = "ucf101"
_C.TRAIN.DATASET = "kinetics"
_C.TRAIN.NUM_DATA_WORKERS = 4


# -----------------------------------------------------------------------------
# Testing options
# -----------------------------------------------------------------------------
_C.TEST = CfgNode()
#_C.TEST.DATASET = "ucf101"
#_C.TEST.BATCH_SIZE = 8


# -----------------------------------------------------------------------------
# Model options
# -----------------------------------------------------------------------------
_C.MODEL = CfgNode()
_C.MODEL.ARCH = "slowfast"
#_C.MODEL.ARCH = "3dresnet"

# -----------------------------------------------------------------------------
# Dataset options
# -----------------------------------------------------------------------------
_C.DATASET = CfgNode()
#_C.DATASET.VID_PATH = '/media/diskstation/datasets/UCF101/jpg'
#_C.DATASET.ANNOTATION_PATH = '/media/diskstation/datasets/UCF101/json/ucf101_01.json'
_C.DATASET.VID_PATH = '/media/diskstation/datasets/kinetics400/frames_shortedge320px_25fps'
_C.DATASET.ANNOTATION_PATH = '/media/diskstation/datasets/kinetics400/vid_paths_and_labels/frame_paths'

_C.DATASET.CHANNEL_EXTENSIONS = ''
_C.DATASET.KEYPOINT_PATH = ''

# -----------------------------------------------------------------------------
# Slowfast options
# -----------------------------------------------------------------------------
_C.SLOWFAST = CfgNode()
_C.SLOWFAST.CFG_PATH = 'models/slowfast/configs/Kinetics/SLOWFAST_8x8_R50.yaml'
_C.SLOWFAST.ALPHA = 4


# -----------------------------------------------------------------------------
# 3dResNet options
# -----------------------------------------------------------------------------
_C.RESNET=CfgNode()
_C.RESNET.MODEL_DEPTH = 18
_C.RESNET.N_CLASSES=1039
_C.RESNET.N_INPUT_CHANNELS = 3
_C.RESNET.SHORTCUT = 'B'
_C.RESNET.CONV1_T_SIZE = 7
_C.RESNET.CONV1_T_STRIDE = 1
_C.RESNET.NO_MAX_POOl = True
_C.RESNET.WIDEN_FACTOR = 1

# -----------------------------------------------------------------------------
# Data options
# -----------------------------------------------------------------------------
_C.DATA = CfgNode()

# The spatial crop size of the input clip.
_C.DATA.SAMPLE_SIZE = 224

# The number of frames of the input clip.
_C.DATA.SAMPLE_DURATION = 8

# Input frame channel dimension.
_C.DATA.INPUT_CHANNEL_NUM = 3


# -----------------------------------------------------------------------------
# Loss Options
# -----------------------------------------------------------------------------
_C.LOSS = CfgNode()
_C.LOSS.MARGIN = 0.5
_C.LOSS.DIST_METRIC = 'cosine'
#_C.LOSS.DIST_METRIC = 'euclidean'


# -----------------------------------------------------------------------------
# Optimizer options
# -----------------------------------------------------------------------------
_C.OPTIM = CfgNode()
_C.OPTIM.LR = 0.05
_C.OPTIM.MOMENTUM = 0.5


# -----------------------------------------------------------------------------
# Misc options
# -----------------------------------------------------------------------------
_C.NUM_GPUS = 1
_C.OUTPUT_PATH = "."


# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------


# Check assertions for the cfg parameters and return the cfg
def _assert_and_infer_cfg(cfg):
    #assert cfg.TRAIN.BATCH_SIZE % cfg.NUM_GPUS == 0
    #assert cfg.TEST.BATCH_SIZE % cfg.NUM_GPUS == 0

    return cfg


def get_cfg():
    """
    Get a copy of the default config.
    """
    return _assert_and_infer_cfg(_C.clone())
