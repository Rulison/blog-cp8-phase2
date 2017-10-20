#!/bin/bash

python preprocess.py -t $1

python data_writer.py -t $1 -o just_model.blog -p params.txt
