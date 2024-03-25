import argparse
import os
import glob
import ast
import pickle

import numpy as np
import tensorflow as tf
from tensorflow.python.summary.summary_iterator import summary_iterator


# View and convert data from tf file saved by rce by default to train.pkl files that lfgp uses
# optionally do for all seeds of a run

parser = argparse.ArgumentParser()
parser.add_argument('--experiment_dir', type=str)
parser.add_argument('--env', type=str)
parser.add_argument('--exp_name', type=str)
parser.add_argument('--main_exp_dir', type=str, default='/media/stonehenge/users/trevor-ablett/rce')
parser.add_argument('--alg_name', type=str, default='rce_theirs')
parser.add_argument('--seeds', type=str, default='[1,2,3,4,5]')


args = parser.parse_args()


# find summary file
if args.experiment_dir:
    eval_dir = os.path.join(args.experiment_dir, 'eval', 'events*')
    files = glob.glob(eval_dir)
    assert len(files) == 1
    eval_tf_sum_files = [files[0]]
    seeds = None
    all_exp_dirs = [args.experiment_dir]
else:
    seeds = ast.literal_eval(args.seeds)
    eval_tf_sum_files = []
    all_exp_dirs = []
    for seed in seeds:
        exp_dir_no_date = os.path.join(args.main_exp_dir, args.env, str(seed), args.alg_name, args.exp_name, '*')
        exp_dirs = sorted(glob.glob(exp_dir_no_date))
        if len(exp_dirs) > 1:
            print(f"WARNING: multiple folders found at {exp_dir_no_date}, taking {exp_dirs[-1]}")
        exp_dir = exp_dirs[-1]
        all_exp_dirs.append(exp_dir)
        eval_dir = os.path.join(exp_dir, 'eval', 'events*')
        files = glob.glob(eval_dir)
        if len(files) > 1:
            print(f"WARNING: Multiple tf events files at {eval_dir}, taking the largest.")
            sizes = []
            for f in files:
                sizes.append(os.stat(f).st_size)
            file = files[np.argmax(sizes)]
        else:
            file = files[0]
        eval_tf_sum_files.append(files[0])

for file_i, file in enumerate(eval_tf_sum_files):
    if seeds is not None:
        seeds = ast.literal_eval(args.seeds)
        print(f"Reading eval for seed {seeds[file_i]}")

    # loop through summary file
    steps = []
    avg_returns = []
    for entry in summary_iterator(file):
        step = entry.step

        for v in entry.summary.value:
            if v.tag == "Metrics/AverageReturn" and step > 0:
                steps.append(step)
                value = tf.make_ndarray(v.tensor)
                avg_returns.append(value.item())

    steps = np.array(steps)
    avg_returns = np.array(avg_returns)

    print(f"Results for ")
    print(f"Steps: {steps}")
    print(f"Avg returns: {avg_returns}")

    # save the file as lfgp format
    data_dict = {
        'mean_evaluation_returns': avg_returns
    }

    pickle.dump(data_dict, open(os.path.join(all_exp_dirs[file_i], 'train.pkl'), 'wb'))
