import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--visualize', '-v', action='store_true')

args = parser.parse_args()

if args.visualize:
    import vis
    vis.run()
else:
    import show
    show.run()