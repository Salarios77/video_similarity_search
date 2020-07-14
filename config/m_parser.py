import argparse
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from default_params import get_cfg


# Argument parser
def parse_args():
    parser = argparse.ArgumentParser("Video Similarity Search Training Script")
    parser.add_argument(
        '--pretrain_path',
        default=None,
        type=str, action='store',
        help='Path to pretrained encoder'
    )
    parser.add_argument(
        '--checkpoint_path',
        default=None,
        type=str, action='store',
        help='Path to checkpoint'
    )
    parser.add_argument(
        "--cfg",
        default=None,
        dest="cfg_file",
        type=str,
        help="Path to the config file",
    )
    parser.add_argument(
        "--output",
        default=None,
        type=str,
    help='output path, overwrite OUTPUT_PATH in default_params.py if specified'
    )
    parser.add_argument(
        "opts",
        default=None,
        nargs=argparse.REMAINDER,
        help="See config/defaults.py for all options",
    )
    return parser.parse_args()


# Get default cfg and merge parameters from cfg file and opts in arguments
def load_config(args):
    cfg = get_cfg()

    if args.cfg_file is not None:
        cfg.merge_from_file(args.cfg_file)

    if args.output:
        cfg.OUTPUT_PATH = args.output
    print('OUTPUT_PATH is set to: {}'.format(cfg.OUTPUT_PATH))

    if args.opts is not None:
        cfg.merge_from_list(args.opts)

    return cfg