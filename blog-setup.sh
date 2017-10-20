#!/bin/bash

sudo apt-get update

# install java
<<<<<<< HEAD
sudo apt-get -y install default-jre

# install javac
sudo apt-get -y install default-jdk
=======
# sudo apt-get -y install default-jre

# install javac
# sudo apt-get -y install default-jdk
>>>>>>> cc2f72d76d07b65f5a3013df1e1114274e6af4c4

# install python2.7
sudo apt-get -y install python-minimal

# one-time setup to read in training data and write blog model representation.
<<<<<<< HEAD
git clone https://github.com/BayesianLogic/blog
cd blog
sbt/sbt compile
sbt/sbt stage
=======
git clone https://github.com/lileicc/swift
cd swift

sudo apt-get -y install make

sudo apt-get -y install g++

sudo apt-get -y install libarmadillo-dev

make compile

mv ../user_util.cpp .
mv ../user_util.h .
>>>>>>> cc2f72d76d07b65f5a3013df1e1114274e6af4c4
cd ..
