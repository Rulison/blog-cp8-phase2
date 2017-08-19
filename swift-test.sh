#!/bin/bash

python data_writer.py -o just_model.blog -p params.txt
python test_writer.py -i just_model.blog -o models -t user02/events_il_mod.json -p "params.txt"
cd swift
./swift -i ../models/user02/events_il_mod.json.blog -o outtest.cpp -e ParticleFilter -n 10000000
mv outtest.cpp src
cd src
g++ -g -Ofast -std=c++11 outtest.cpp random/*.cpp -o outtest -larmadillo
./outtest
cd ../..
