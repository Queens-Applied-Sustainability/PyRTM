
from os import path, getcwd

WORKING_DIR = path.join(getcwd(), 'pyrtm', 'sbdart', 'exe')
EXECUTABLE = 'drtx'
INPUT_FILE = 'INPUT'
OUTPUT_FILE = 'OUTPUT'

EXAMPLE_INPUTS = {
    'tcloud': '$tcloud',
    'zcloud': 8,
    'nre': 10,
    'idatm': 4,
    'sza': 95,
    'wlinf': 4,
    'wlsup': 20,
    'wlinc': -.01
}
