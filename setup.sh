#!/usr/bin/env bash
export DOWNLOAD_KERNELS_FOLDER="downloaded_kernels/"
export KERNELS_RUNNER_FOLDER="runner/"
export S3_BUCKET="https://transfer-snippets.s3.us-east-2.amazonaws.com"
export CONDA_TRANSFER_ENV="transfer-env"
export DOCKER_RUNNER_IMAGE="cleaning"

function check_transfer_conda_env {
  echo $(conda env list | grep ${CONDA_TRANSFER_ENV} | wc -l)
}

function activate_transfer_conda_env {
    if command -v conda
    then
       config_path=$(realpath "$(dirname $(which conda))/../etc/profile.d")
       source "${config_path}/conda.sh"
       conda activate ${CONDA_TRANSFER_ENV}
    fi
}

function create_transfer_conda_env {
  if command -v conda
  then
    if [ $(check_transfer_conda_env) -eq 0 ]
    then
      # install if missing
      echo "Building conda environment: transfer-env"
      yes | conda create -n ${CONDA_TRANSFER_ENV} python=3.7
    fi
  fi
}