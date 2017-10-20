#!/bin/bash

for var in "$@"
do
	python test_writer.py -i just_model.blog -o models -t "$var" -p "params.txt"
	cd swift
	./swift -i "../models/$var.blog" -o outtest.cpp -e ParticleFilter --particle 100000
	mv outtest.cpp src
	cd src
	g++ -g -Ofast -std=c++11 outtest.cpp random/*.cpp -o outtest -larmadillo --include ../user_util.h ../user_util.cpp
	./outtest > "../../$var.out"
	cd ../..
	echo "finished blog inference for $var"
	python json_maker_final.py -i "$var.out" -o "out/$var" -t "$var"
	echo "finished processing $var"
done
python name_fixer.py -i "out"
