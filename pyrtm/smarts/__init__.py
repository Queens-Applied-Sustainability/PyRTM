"""Set up some basic info for SMARTS

blah blah more about smarts
"""

from os import path, getcwd

VERSION = (2, 9, 5, 'final')
WORKING_DIR = 'exe'
EXECUTABLE = 'smarts295'
EXECUTABLE_PATH = path.join(WORKING_DIR, EXECUTABLE)

# KISS -- stick to SMARTS' defaults.
INPUT_FILE = path.join(EXECUTABLE)
OUTPUT_FILE = path.join(EXECUTABLE)

# These values are generated to match the ones SMARTS will auto-generate.
INPUT_FILE_FULL = '.'.join([INPUT_FILE, 'inp', 'txt'])
OUTPUT_FILE_FULL = '.'.join([OUTPUT_FILE, 'out', 'txt'])
OUTPUT_FILE_SPREAD = '.'.join([OUTPUT_FILE, 'ext', 'txt'])
OUTPUT_FILE_SMOOTHED = '.'.join([OUTPUT_FILE, 'scn', 'txt'])

WD = getcwd()
EWD = path.join(WD, WORKING_DIR)
