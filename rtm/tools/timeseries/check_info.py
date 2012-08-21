"""check the file..."""

import sys
from rtm import settings


REQUIRED = {
	'station_info': ['latitude', 'longitude', 'elevation'],
	'column_map': ['time', 'irrad'],
}


class InfoParseError(SystemExit): pass
class InfoMissingError(SystemExit): pass


def check(module):
	"""validate a user's configuration"""

	# can we import the settings?
	try:
		info = __import__(module)
	except ImportError:
		raise InfoParseError('ERROR: Could not import config: %s.' % module)
	except SyntaxError as err:
		import re
		print 'Syntax error on line %d in %s: %s' % (err.lineno, module,
			err.msg)
		line, tabs = re.subn(r'\t', '    ', err.text)
		print line,
		print ' ' * (err.offset - 1 + tabs * 3) + '^'
		sys.exit(1)

	# is there a dict containing station_info?
	try:
		station_info = info.station_info
	except AttributeError:
		raise InfoParseError('ERROR: Could not find "station_info" in %s.' %
			module)

	# is all the required station_info present?
	for required_info in REQUIRED['station_info']:
		if required_info not in station_info:
			raise InfoMissingError('ERROR: setting "%s" is required in the '\
				'station_info dict.' % required_info)

	# are all the station_info settings understood?
	for sinfo in station_info:
		if sinfo not in settings.defaults:
			print 'Warning: "%s" is not a model input parameter' % sinfo

	# is the column_map present?
	try:
		cmap = info.column_map
	except AttributeError:
		raise InfoParseError('ERROR: Could not find "column_map" in %s.' %
			module)

	# are the required columns present?
	for required_column in REQUIRED['column_map']:
		if required_column not in cmap:
			if required_column is 'time':
				if 'date' in [v for k, v in cmap.items()] and\
					'hour' in [v for k, v in cmap.items()]:
					continue
			raise InfoMissingError('ERROR: setting %s is required in the '\
				'"colum_map" dict' % required_column)

	# are all the columns understood?
	for column in cmap:
		if column not in settings.defaults:
			print 'Warning: "%s" is not a model input parameter' % column


if __name__ == '__main__':
	try:
		infile = sys.argv[2]
	except IndexError:
		module = 'info'
	else:
		module = infile[:-3] if infile.endswith('.py') else infile

	check(module)
