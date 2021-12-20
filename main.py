from getopt import getopt
import sys

opts, args = getopt(sys.argv[1:], "v")

if "-v" in opts:
    import vis
    vis.run()
else:
    import show
    show.run()