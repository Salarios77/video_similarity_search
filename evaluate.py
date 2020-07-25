"""
Created by Sherry Chen on Jul 14, 2020
retrieve the most similar clips
"""
import os
import argparse
import pprint
import time
import numpy as np
import random
import torch
import cv2
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics.pairwise import euclidean_distances
from datasets import data_loader
from models.triplet_net import Tripletnet
from models.model_utils import model_selector, multipathway_input
from datasets.data_loader import build_spatial_transformation
from datasets.temporal_transforms import TemporalCenterFrame, TemporalSpecificCrop
from datasets.temporal_transforms import Compose as TemporalCompose
from config.m_parser import load_config, parse_args
from train import load_checkpoint

num_exempler = 5
log_interval = 10
top_k = 5
split = 'val'
exempler_file = None 
# exempler_file = '/home/sherry/output/evaluate_exempler.txt'

def evaluate(model, test_loader, log_interval=5):
    model.eval()
    embedding = []
    vid_info = []
    with torch.no_grad():
        for batch_idx, (input, targets, info) in enumerate(test_loader):
            # if batch_idx > 1:
            #     break
            batch_size = input.size(0)

            if cfg.MODEL.ARCH == 'slowfast':
                input = multipathway_input(input, cfg)
                if cuda:
                    for i in range(len(input)):
                        input[i] = input[i].to(device)
            else:
                if cuda:
                    input= input.to(device)

            embedd = model(input)
            embedding.append(embedd.detach().cpu())
            vid_info.extend(info)
            # print('embedd size', embedd.size())
            if batch_idx % log_interval == 0:
                print('val [{}/{}]'.format(batch_idx * batch_size, len(test_loader.dataset)))

    embeddings = torch.cat(embedding, dim=0)
    return embeddings


def get_distance_matrix(embeddings):
    print('embeddings size', embeddings.size())
    embeddings = embeddings
    distance_matrix = euclidean_distances(embeddings)
    print('distance matrix shape:', distance_matrix.shape)

    np.fill_diagonal(distance_matrix, float('inf'))
    return distance_matrix


def get_closest_data(distance_matrix, exempler_idx, top_k):
    test_array = distance_matrix[exempler_idx]
    idx = np.argpartition(test_array, top_k)
    top_k = idx[np.argsort(test_array[idx[:top_k]])]
    return top_k


def plot_img(cfg, fig, data, num_exempler, row, exempler_idx, k_idx, spatial_transform=None, temporal_transform=None, output=None):
    exempler_frame = data._loading_img_path(exempler_idx, temporal_transform)
    test_frame = [data._loading_img_path(i, temporal_transform) for i in k_idx]

    exempler_title = '-'.join(exempler_frame.split('/')[-3:-2])

    print(exempler_frame)
    print('top k ids:', end=' ')
    for i in k_idx:
        print(i, end=' ')
    print()
    pprint.pprint(test_frame)

    ax = fig.add_subplot(num_exempler,len(test_frame)+1, row*(len(test_frame)+1)+1)
    image = plt.imread(exempler_frame)
    plt.imshow(image)
    ax.set_title(exempler_title, fontsize=5, pad=0.3)
    plt.axis('off')
    for i in range(len(test_frame)):
        test_title = '-'.join(test_frame[i].split('/')[-3:-2])
        ax = fig.add_subplot(num_exempler,len(test_frame)+1, row*(len(test_frame)+1)+i+2)
        image = plt.imread(test_frame[i])
        plt.imshow(image)
        ax.set_title(test_title, fontsize=5, pad=0.3)
        plt.axis('off')

    with open(os.path.join(output, 'results.txt'), 'a') as f:
        f.write('exempler_frame:\n{}\n'.format(exempler_frame))
        for frame in test_frame:
            f.write(frame)
            f.write('\n')
        f.write('\n')

    with open(os.path.join(output, 'exempler.txt'), 'a') as f:
        f.write('{}, {}'.format(exempler_idx, exempler_frame))
        f.write('\n')

def load_exempler(exempler_file):
    with open(exempler_file, 'r') as f:
        lines = f.readlines()
    exempler_idx  = []
    for line in lines:
        exempler_idx.append(int(line.split(',')[0].strip()))
    return exempler_idx

def k_nearest_embeddings(model, test_loader, data, cfg, evaluate_output):
    embeddings = evaluate(model, test_loader, log_interval=log_interval)

    distance_matrix = get_distance_matrix(embeddings)

    spatial_transform = build_spatial_transformation(cfg, split)
    temporal_transform = [TemporalCenterFrame()]
    temporal_transform = TemporalCompose(temporal_transform)
    
    if exempler_file:
        exempler_indices = load_exempler(exempler_file)
        num_exempler = len(exempler_indices)
        print('exempler_idx retrieved: {}'.format(exempler_indices))
        print('number of exemplers is: {}'.format(num_exempler))
        
    fig = plt.figure()
    for i in range(num_exempler):
        if not exempler_file:
            exempler_idx = random.randint(0, distance_matrix.shape[0]-1)
        else:
            exempler_idx = exempler_indices[i]
            
        print('exempler video id: {}'.format(exempler_idx))
        k_idx = get_closest_data(distance_matrix, exempler_idx, top_k)
        k_nearest_data = [data[i] for i in k_idx]
        plot_img(cfg, fig, data, num_exempler, i, exempler_idx, k_idx, spatial_transform, temporal_transform, output=evaluate_output)
    # plt.show()
    png_file = os.path.join(evaluate_output, 'plot.png')
    fig.tight_layout(pad=3.5)
    plt.savefig(png_file)
    print('figure saved to: {}'.format(png_file))


def temporal_heat_map(model, data, cfg, evaluate_output):
    exemplar_idx = 455
    test_idx = 456

    num_frames_exemplar = data.data[exemplar_idx]['num_frames']

    exemplar_video_full, _, _ = data._get_video_custom_temporal(exemplar_idx)  # full size
    exemplar_video_full = exemplar_video_full.unsqueeze(0)

    num_frames_crop = cfg.DATA.SAMPLE_DURATION
    stride = num_frames_crop // 2
    dists = []

    model.eval()
    with torch.no_grad():
        test_video, _, _ = data.__getitem__(test_idx)  # cropped size
        test_video = test_video.unsqueeze(0)
        print('Test input size:', test_video.size(), '\n')
        if (cfg.MODEL.ARCH == 'slowfast'):
            test_video_in = multipathway_input(test_video, cfg)
            if cuda:
                for i in range(len(test_video_in)):
                    test_video_in[i] = test_video_in[i].to(device)
        else:
            if cuda:
                test_video_in = test_video_in.to(device)
        test_embedding = model(test_video_in)
        #print('Test embed size:', test_embedding.size())
 
        # Loop across exemplar video, use [i-cfg.DATA.SAMPLE_SIZE,...,i] as the frames for the temporal crop
        for i in range(num_frames_crop, num_frames_exemplar, stride):
            temporal_transform_exemplar = TemporalSpecificCrop(begin_index=i-num_frames_crop, size=num_frames_crop)
            exemplar_video, _, _ = data._get_video_custom_temporal(exemplar_idx, temporal_transform_exemplar)  # full siz
            exemplar_video = exemplar_video.unsqueeze(0)
            
            if (cfg.MODEL.ARCH == 'slowfast'):
                exemplar_video_in = multipathway_input(exemplar_video, cfg)
                if cuda:
                    for j in range(len(exemplar_video_in)):
                        exemplar_video_in[j] = exemplar_video_in[j].to(device)                
            else:
                if cuda:
                    exemplar_video_in = exemplar_video_in.to(device)

            exemplar_embedding = model(exemplar_video_in)
            #print('Exemplar input size:', exemplar_video.size())
            #print('Exemplar embed size:', exemplar_embedding.size())
            dist = F.pairwise_distance(exemplar_embedding, test_embedding, 2)
            dists.append(dist.item())
        
    #print(dists)
    x = []
    y = []
    plt.show()
    axes = plt.gca()
    axes.set_xlim(0, num_frames_exemplar)
    axes.set_ylim(0, max(dists))
    line, = axes.plot(x, y, 'b-')
    dist_idx = 0

    # channels x frames x width, height --> frames x width x height x channels
    video_ex = exemplar_video_full[0].permute(1,2,3,0)
    video_test = test_video[0].permute(1,2,3,0)
    fps = 25.0
    for i in range(len(video_ex)):
        blank_divider = np.full((2,128,3), 256, dtype=int)
        np_vertical_stack = np.vstack(( video_ex[i].numpy(), blank_divider, video_test[i % len(video_test)].numpy() ))
        cv2.imshow('Videos', np_vertical_stack)

        # show plot of embedding distance for past num_frames_crop frames of exemplar video
        if i >= num_frames_crop and (i - num_frames_crop) % stride == 0:
            x.append(i)
            y.append(dists[dist_idx])
            line.set_xdata(x)
            line.set_ydata(y)
            plt.draw()
            plt.pause(1e-17)
            dist_idx += 1

        cv2.waitKey(int(1.0/fps*1000.0))
        

if __name__ == '__main__':
    args = parse_args()
    cfg = load_config(args)

    force_data_parallel = True

    os.environ["CUDA_VISIBLE_DEVICES"]=str(args.gpu)
    global cuda; cuda = torch.cuda.is_available()
    global device; device = torch.device("cuda" if cuda else "cpu")

    start = time.time()

    now = datetime.now()
    evaluate_output = os.path.join(args.output, 'evaluate_{}'.format(now.strftime("%d_%m_%Y_%H_%M_%S")))
    if not os.path.exists(evaluate_output):
        os.makedirs(evaluate_output)
        print('made output dir:{}'.format(evaluate_output))

    # ============================== Model Setup ===============================

    model=model_selector(cfg)
    print('=> finished generating {} backbone model...'.format(cfg.MODEL.ARCH))

    tripletnet = Tripletnet(model)
    if cuda:
        if torch.cuda.device_count() > 1 or force_data_parallel:
            print("Let's use {} GPUs".format(torch.cuda.device_count()))
            tripletnet = nn.DataParallel(tripletnet)

    if args.checkpoint_path is not None:
        start_epoch, best_acc = load_checkpoint(tripletnet, args.checkpoint_path)

    model = tripletnet.module.embeddingnet
    if cuda:
        model.to(device)

    print('=> finished generating similarity network...')

    # ============================== Data Loaders ==============================

    test_loader, data = data_loader.build_data_loader(split, cfg, triplets=False)
    print()

    # ================================ Evaluate ================================

    k_nearest_embeddings(model, test_loader, data, cfg, evaluate_output)
    print('total runtime: {}s'.format(time.time()-start))

    #temporal_heat_map(model, data, cfg, evaluate_output)
    