#!/bin/bash

# Code for running multiple seeds and configurations in series

# e.g. bash all_seeds.bash sawyer_drawer_open mar23 0

env=$1
exp_name=$2
gpu_i=$3
seeds=(1 2 3 4 5)

echo "Starting for loop of execution with args $@"
for seed in "${seeds[@]}"; do
    echo "Running seed ${seed}, env ${env}"
    date_str=$(date '+%m-%d-%y_%H_%M_%S')

    case ${env} in
        "relocate-human-v0")
            num_steps=1500000
            ;;
        "sawyer_drawer_open" | "sawyer_bin_picking" | "door-human-v0" | "sawyer_drawer_close")
            num_steps=300000
            ;;
        "sawyer_push" | "sawyer_lift" | "sawyer_box_close" | "hammer-human-v0")
            num_steps=500000
            ;;
        *)
            echo "unknown env! exiting"
            exit 1
            ;;
    esac

    python_args=(
        --root_dir="/media/stonehenge/users/trevor-ablett/rce/${env}/${seed}/rce_theirs/${exp_name}/${date_str}"
        --gin_bindings="train_eval.env_name=\"${env}\""
        --gin_bindings="train_eval.num_iterations=${num_steps}"
        --gin_bindings="train_eval.gpu_i=${gpu_i}"
    )

    if [ ${env} = "sawyer_bin_picking" ]; then
        python_args+=(--gin_bindings='critic_loss.q_combinator="max"')
        python_args+=(--gin_bindings='actor_loss.q_combinator="max"')
    fi

    echo "All args: ${python_args[@]}"

    python train_eval.py "${python_args[@]}"
done