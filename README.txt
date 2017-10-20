BLOG submission for CP8 Phase 2

Tested on an AWS t2.medium instance.  Minimum 2GiB memory.

./blog-setup.sh installs Java, Python, and a version of Blog (in Java).

./run-submission.sh [test files ...] translates each test file to Blog input, runs the Blog inference engine, then formats the output in the specified json format.

./setup-and-run.sh [test files ...] runs both of the above scripts.

[test files] are expected to be in the format userNN/whatever.

python run-all-in-dir.py -t [test_dir] runs on all directories of format userNN inside test_dir.  Inside each user folder, it tries to evaluate events-il-high.json, events-il-med.json, events-il-low.json, and events-il.json.  This can be modified by the files_to_test list inside the python file.

./train.sh [training_dir] redoes training on a directory containing directories of format userNN.

An example command is:
./setup-and-run.sh user35/USER_35.in.json user38/USER_38.in.json.
