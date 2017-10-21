#!/bin/bash

sudo apt-get update


# install python2.7
sudo apt-get -y install python-minimal

git clone https://github.com/lileicc/swift
cd swift

sudo apt-get -y install make

sudo apt-get -y install g++

sudo apt-get -y install libarmadillo-dev

make compile

cp ../user_util.cpp .
cp ../user_util.h .

cd ..
