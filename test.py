#!/usr/bin/env python


if __name__ == '__main__':

	import argparse as ap
	from argparse import Action as _Action


	class TestClass(object):
		"""Code testing class.
		"""

		def print_message(self, arguments):
			print arguments
	

	class VersionAction(_Action):
		"""
		"""
		
		def __call__(self, parser, namespace, values, option_string=None):
			print "Version action is running."
			_Action.__call__(self, parser, namespace, values, option_string)


	parser = ap.ArgumentParser(
		prog='test.py',
		description='This is main program description.',
		epilog='This is main program epilog.',
		formatter_class=ap.RawDescriptionHelpFormatter
	)
	
	generalArgumentsGroup = parser.add_argument_group(
		title='general options',
		description=None
		)

	parser.add_argument(
		'--usage',
		action='store_true',
		help='give short usage message'
	)

	generalArgumentsGroup.add_argument(
		'-V', '--version',
		action=VersionAction,
		nargs=0,
		help='print program version'
		)

	subparsers = parser.add_subparsers(
		title='The test.py can be called with following commands',
		dest='command',
		metavar='',
	)

	loginParser = subparsers.add_parser(
		'login',
		description='This is login command description.',
		epilog='This is login command epilog.',
		help='This is login help.',
		formatter_class=ap.RawDescriptionHelpFormatter
	)

	tobj = TestClass()

	logoutParser = subparsers.add_parser(
		'logout',
		description='This is logout command description.',
		epilog='This is logout command epilog.',
		help='This is logout help.',
		formatter_class=ap.RawDescriptionHelpFormatter
	)
	logoutParser.set_defaults(func=tobj.print_message)

	logoutParser.add_argument(
		'-u', '--username',
		action='store_true',
		help='user to logout'
	)

	args = parser.parse_args()
	args.func(args)
	parser.exit()
