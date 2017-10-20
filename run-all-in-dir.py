import argparse
import os
import fnmatch

from subprocess import call


parser = argparse.ArgumentParser(description="Run submission on all users in directory")
parser.add_argument('-t', '--test_dir',
                    help="Directory containing test folders of format user\d\d")

args = parser.parse_args()

test_dir = args.test_dir
folders = [f for f in os.listdir(test_dir) if fnmatch.fnmatch(f, 'user**')]

files_to_test = ['events-il-high.json', 'events-il-med.json', 'events-il-low.json', 'events-il.json']

for folder in folders:
    for f in files_to_test:
        path = os.path.join(test_dir, folder, f)
        call(["./run-submission.sh", path])
