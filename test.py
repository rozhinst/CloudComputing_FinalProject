import sys
from colorit import *

def handle_file(path, is_number=True):
        data = []
        with open(path) as f:
                for line in f:
                        print(color(line, Colors.blue))

handle_file(sys.argv[1])
