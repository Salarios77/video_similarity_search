"""
Created by Sherry Chen on Jul 3, 2020
Load training and validation data and apply temporal/spatial transformation
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'))

import torch
from torch import nn
from spatial_transforms import (Compose, Normalize, Resize, CenterCrop,
                                CornerCrop, MultiScaleCornerCrop,
                                RandomResizedCrop, RandomHorizontalFlip,
                                ToTensor, ScaleValue, ColorJitter,
                                PickFirstChannels)
from temporal_transforms import (LoopPadding, TemporalRandomCrop,
                                 TemporalCenterCrop, TemporalEvenCrop,
                                 TemporalEndCrop, TemporalBeginCrop,
                                 SlidingWindow, TemporalSubsampling)
from temporal_transforms import Compose as TemporalCompose
from data_utils import Logger, worker_init_fn, get_lr
from dataset import get_data

from m_parser import load_config, parse_args  # from ../config/m_parser


train_crop_min_scale = 0.25
train_crop_min_ratio = 0.75
n_val_samples = 3 # number of validation samples for each activity

video_path = '/media/diskstation/datasets/UCF101/jpg'
annotation_path = '/media/diskstation/datasets/UCF101/json/ucf101_01.json'
input_type = 'rgb'
file_type = 'jpg'
n_threads = 4

no_mean_norm=False
no_std_norm=False
mean_dataset = 'kinetics'
value_scale = 1

ntriplets_train = 9000
ntriplets_val = 1000
distributed=False


def get_mean_std(value_scale, dataset):
    assert dataset in ['activitynet', 'kinetics', '0.5']

    if dataset == 'activitynet':
        mean = [0.4477, 0.4209, 0.3906]
        std = [0.2767, 0.2695, 0.2714]
    elif dataset == 'kinetics':
        mean = [0.4345, 0.4051, 0.3775]
        std = [0.2768, 0.2713, 0.2737]
    elif dataset == '0.5':
        mean = [0.5, 0.5, 0.5]
        std = [0.5, 0.5, 0.5]

    mean = [x * value_scale for x in mean]
    std = [x * value_scale for x in std]

    return mean, std


def get_normalize_method(mean, std, no_mean_norm, no_std_norm):
    if no_mean_norm:
        if no_std_norm:
            return Normalize([0, 0, 0], [1, 1, 1])
        else:
            return Normalize([0, 0, 0], std)
    else:
        if no_std_norm:
            return Normalize(mean, [1, 1, 1])
        else:
            return Normalize(mean, std)


def build_data_loader(split, cfg):
    mean, std = get_mean_std(value_scale, dataset=mean_dataset)
    
    normalize = get_normalize_method(mean, std, no_mean_norm,
                                     no_std_norm)

    assert split in ['train', 'val', 'test']
    if split == 'train':
        n_triplets = ntriplets_train

        spatial_transform = []
        spatial_transform.append(
            RandomResizedCrop(cfg.DATA.SAMPLE_SIZE, (train_crop_min_scale, 1.0),
                            (train_crop_min_ratio, 1.0/train_crop_min_ratio))
            )
        spatial_transform.append(RandomHorizontalFlip())
        spatial_transform.append(ToTensor())
        spatial_transform.append(normalize)

    elif split == 'val':
        n_triplets = ntriplets_val

        spatial_transform = [
            Resize(cfg.DATA.SAMPLE_SIZE),
            CenterCrop(cfg.DATA.SAMPLE_SIZE),
            ToTensor()
        ]
        spatial_transform.extend([ScaleValue(value_scale), normalize])

        # temporal_transform = []
        # # if sample_t_stride > 1:
        # #     temporal_transform.append(TemporalSubsampling(sample_t_stride))
        # temporal_transform.append(TemporalEvenCrop(cfg.DATA.SAMPLE_DURATION, n_val_samples))
        # temporal_transform = TemporalCompose(temporal_transform)

    spatial_transform = Compose(spatial_transform)

    TempTransform = {}
    #anchor
    begin_temporal_transform = []
    begin_temporal_transform.append(TemporalBeginCrop(cfg.DATA.SAMPLE_DURATION))
    begin_temporal_transform = TemporalCompose(begin_temporal_transform)
    TempTransform['anchor'] = begin_temporal_transform

    #positive
    end_temporal_transform = []
    end_temporal_transform.append(TemporalEndCrop(cfg.DATA.SAMPLE_DURATION))
    end_temporal_transform = TemporalCompose(end_temporal_transform)
    TempTransform['positive'] = end_temporal_transform

    #negative
    temporal_transform = []
    temporal_transform.append(TemporalRandomCrop(cfg.DATA.SAMPLE_DURATION))
    temporal_transform = TemporalCompose(temporal_transform)
    TempTransform['negative'] = temporal_transform

    data, collate_fn = get_data(split, cfg.OUTPUT_PATH, video_path, annotation_path,
                cfg.TRAIN.DATASET, input_type, file_type, n_triplets, True,
                spatial_transform, TempTransform)

    if split == 'train':
        sampler = None
        data_loader = torch.utils.data.DataLoader(data,
                                                  batch_size=cfg.TRAIN.BATCH_SIZE,
                                                  shuffle=(sampler is None),
                                                  num_workers=n_threads,
                                                  pin_memory=True,
                                                  sampler=sampler,
                                                  worker_init_fn=worker_init_fn)
    elif split == 'val':
        #TODO: investigate torch.utils.data.distributed.DistributedSampler()
        sampler = None
        data_loader = torch.utils.data.DataLoader(data,
                                                  batch_size = (cfg.TRAIN.BATCH_SIZE // n_val_samples),
                                                  # batch_size = cfg.TRAIN.BATCH_SIZE,
                                                  shuffle=False,
                                                  num_workers=n_threads,
                                                  pin_memory=True,
                                                  sampler=sampler,
                                                  worker_init_fn=worker_init_fn
                                                  # collate_fn=collate_fn)
                                                  )

    return data_loader


if __name__ == '__main__':
    args = parse_args()
    cfg = load_config(args)

    train_loader = build_data_loader('train', cfg)
    val_loader = build_data_loader('val', cfg)

    # print(train_loader)
    # for i, (inputs, targets) in enumerate(train_loader):
    #     if i>3:
    #         break
    #     print(i, inputs.shape, targets)

    # for i, data in enumerate(train_loader):
    #     a, b = data
    #     x, y, z = a
    #     print(x.shape)
