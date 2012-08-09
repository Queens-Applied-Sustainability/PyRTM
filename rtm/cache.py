"""
file cacheing for rtm stuff.


cacheing directory structure

[desc]-[lng]-[lat]\
	[year]-[month]\
		[fname]-[datetime].pkl


2012-03-12_16_30_00.pkl:

{
	'config': {...},
	'solution': {
		'AOD': 0.XX,
		'cloud': X.X
	},
	'spectrum': numpy.Array()
}


"""

import re
import os
import cPickle as pickle
from superhash import superhash


MAX_FILE_CHARS = 42
CACHE_DIR = 'cached'
ROOT = ['description', 'longitude', 'latitude']
SECONDARY = ['year', 'month']


def vars_to_file(vars):
	"""Return a safe string to be used as a file or directory name"""
	clean_vars = [re.sub('[^a-zA-Z0-9_:]', '.', str(v)) for v in vars]
	clean_string = '-'.join(clean_vars)
	if len(clean_string) > MAX_FILE_CHARS:
		# name was too long; use hash instead hash instead.
		return str(clean_string.__hash__())
	return clean_string


def get(f, config):
	root = vars_to_file(config[v] for v in ROOT)
	secondary = vars_to_file(getattr(config['time'], v) for v in SECONDARY)

	filename = vars_to_file([f.__name__, superhash(config)])

	path = os.path.join(CACHE_DIR, root, secondary)

	# assume the value is cached: try to read it
	try:
		f_out = pickle.load(open(os.path.join(path, filename), 'rb'))
		hit = True

	except IOError:
		# nothing cached. run the function
		f_out = f(config)

		# assume the directories are already set up
		try:
			cachefile = open(os.path.join(path, filename), 'wb')

		except IOError:
			# probably the path is not set up correctly. Set it up...
			os.makedirs(path)
			cachefile = open(os.path.join(path, filename), 'wb')

		pickle.dump(f_out, cachefile)
		hit = False

	return f_out, hit


