BLOG submission for CP8 Phase 2

Tested on an AWS t2.medium instance.  Minimum 4GiB memory.

./blog-setup.sh installs g++, Python, make, armadillo, and the swift BLOG compiler.

./run-submission.sh [test files ...] translates each test file to Blog input, runs the Blog inference engine, then formats the output in the specified json format.

./setup-and-run.sh [test files ...] runs both of the above scripts.

[test files] are expected to be in the format userNN/whatever.

An example command is:
./setup-and-run.sh user35/USER_35.in.json user38/USER_38.in.json.
