import sys
import os
basedir = os.path.dirname(__file__)
sys.path.append(os.path.dirname(basedir))

OUTPUT_DIR = os.path.join(basedir, "output")
OUTPUT_DIR_FIGURES = os.path.join(OUTPUT_DIR, "figures")
OUTPUT_DIR_DATA = os.path.join(OUTPUT_DIR, "data")
if os.path.exists(OUTPUT_DIR_FIGURES):
    os.makedirs(OUTPUT_DIR_FIGURES)
if os.path.exists(OUTPUT_DIR_DATA):
    os.makedirs(OUTPUT_DIR_DATA)

def is_pypy():
    return sys.version.lower().find("pypy") != -1
