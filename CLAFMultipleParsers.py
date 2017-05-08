#!/usr/bin/env python
#==============================================================================
# <one line to give the program's name and a brief idea of what it does.>
#
#  Copyright (C) <yyyy> <Author Name> <author@mail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#==============================================================================


#==============================================================================
#
# <Put documentation here>
#
# <yyyy>-<mm>-<dd> <Author Name> <author@mail.com>
#
# * <programfilename>.py: created.
#
#==============================================================================


import argparse


#==============================================================================
# Utility classes and functions
#==============================================================================

def _format_epilog(epilogAddition, bugMail):
	"""Formatter for generating help epilogue text. Help epilogue text is an
	additional description of the program that is displayed after the
	description of the arguments. Usually it consists only of line informing
	to which email address to report bugs to, or it can be completely
	omitted.

	Depending on provided parameters function will properly format epilogue
	text and return string containing formatted text. If none of the
	parameters are supplied the function will return None which is default
	value for epilog parameter when constructing parser object.
	"""

	fmtAdition = None
	fmtMail = None
	fmtEpilog = None

	if None == epilogAddition and None == bugMail:
		return None

	if None != bugMail:
		fmtMail = 'Report bugs to <{bugMail}>.'\
			.format(bugMail = bugMail)
	else:
		fmtMail = None

	if None == epilogAddition:
		fmtEpilog = fmtMail

	elif None == fmtMail:
		fmtEpilog = epilogAddition

	else:
		fmtEpilog = '{addition}\n\n{mail}'\
			.format(addition = epilogAddition, mail = fmtMail)

	return fmtEpilog


def _formulate_action(Action, **kwargs):
	"""Factory method to create and return proper action object.
	"""

	return Action(**kwargs)


#==============================================================================
# Program classes
#==============================================================================

class _Program(object):
	"""Abstract base class for MainProgram and SubProgram classes.
	
	Every app can be divided into main program and number of subprograms
	(subcommands). This class defines common properties for both types of
	objects.

	This class or its subclasses should not implement any methods (except
	constructor) for accessing its properties, this is done elsewhere
	(CommandLineApp class). The sole purpose of this classes and its
	subclasses is to group relevant data for parser and each of subparsers.
	"""

	def __init__(self):
		self.parser = None
		self.argumentGroups = list()


class _MainProgram(_Program):
	"""
	"""

	def __init__(self):
		_Program.__init__(self)
		self.subParsers = None


class _SubProgram(_Program):
	"""
	"""

	def __init__(self):
		self.parser = None
		self.argumentGroups = list()


#==============================================================================
# Command line app class
#==============================================================================

class CommandLineApp(object):
	"""Actual command line app object containing all relevant application
	information (NAME, VERSION, DESCRIPTION, ...) and which instantiates
	action that will be executed depending on the user input from
	command line.
	"""

	def __init__(self,
		programName=None,
		programDescription=None,
		programLicense=None,
		versionString=None,
		yearString=None,
		authorName=None,
		authorMail=None,
		epilog=None):

		self.programLicense = programLicense
		self.versionString = versionString
		self.yearString = yearString
		self.authorName = authorName
		self.authorMail = authorMail

		fmtEpilog = _format_epilog(epilog, authorMail)

		self._parsers['main'] = _MainProgram()
		self._parsers['main'].parser = argparse.ArgumentParser(
			prog = programName,
			description = programDescription,
			epilog = fmtEpilog,
			formatter_class=argparse.RawDescriptionHelpFormatter
			)

		self._ation = None


	@property
	def programName(self):
		"""Utility function that makes accessing program name attribute
		neat and hides implementation details.
		"""
		return self._parsers['main'].parser.prog


	@property
	def programDescription(self):
		"""Utility function that makes accessing program description
		attribute neat and hides implementation details.
		"""
		return self._parsers['main'].parser.description


	def add_subparsers(self, title=None):
		"""Wrapper for add_parsers method of ArgumentParser class. This
		method is provided to enable custom subparsers title setup. If
		'title' parameter is not provided (None) default value is used.
		"""

		if None == title:
			title = \
			'The {0} can be called with following commands:'\
			.format(self._paser.prog.strip('.py'))

		# Make an alias to ease referencing a bit.
		mp = self._parsers['main'].parser

		mp.subParsers = mainparser.add_parsers(
			title=title,
			dest='command',
			metavar='')


	def add_subcommand(self,
		commandName=None,
		commandDescription=None,
		commandEpilog=None,
		commandHelp=None
		):
		"""
		"""
		# Do some sanity checks first.
		if None == self._parsers['main'].subParsers:
			raise ValueError('Subparser object not initialized.')
		sp = self._parsers['main'].subParsers

		if None == commandName:
			raise NameError('Missing command name.')

		if commadName in self._parsers:
			raise ValueError(
				'Duplicate entry. Command name already exists.'
				)

		epilogFmtd = _format_epilog(commandEpilog, self.authorMail)

		self._parsers[commandName] = _SubProgram()
		p = self._parsers[commandName].parser
		p = sp.add_parser(
			commandName,
			description = commandDescription,
			epilog = epilogFmtd,
			help=commandHelp,
			formatter_class=argparse.RawDescriptionHelpFormatter
			)


	def add_argument_group(self, title=None, description=None, parser='main'):
		"""Adds an argument group to a given parser or the main parser
		if no paser is supplied.
		At least group title must be provided or method will rise
		NameError exception. This is to prevent creation of titleless
		and descriptionless argument groups. Although this is allowed by
		argparse module I don't see any use of a such utility."""

		if parser not in self._parsers:
			raise ValueError(
				'Trying to reference nonexistent parser.'
				)

		if None == title:
			raise NameError('Missing arguments group title.')

		p = self._parsers[parser]
		group = p.add_argument_group(title, description)
		p.argumentGroups.append(group)


	def _group_by_title(self, title, parser='main'):

		if parser not in self._parsers:
			raise ValueError(
				'Trying to reference nonexistent parser.'
				)

		p = self._parsers[parser]
		group = None

		for item in p.argumentGroups:
			if title == item.title:
				group = item
				break

		return group


	def add_argument(self, *args, **kwargs):
		"""Wrapper for add_argument methods of argparse module. If
		parameter group is supplied with valid group name, argument will
		be added to that group. If group parameter is omitted argument
		will be added to parser object. In a case of invalid group name
		it rises ValueError exception.
		"""

		paser = 'main'
		if 'parser' in kwargs:
			parser = kwargs.pop('parser')
		if parser not in self._parsers:
			raise ValueError(
				'Trying to reference nonexistent parser.'
				)
		p = self._parsers[parser]

		if 'group' not in kwargs or None == kwargs['group']:
			p.add_argument(*args, **kwargs)

		else:
			group = self._group_by_title(
				kwargs.pop('group'),
				parser
				)

			if None == group:
				raise ValueError(
				'Trying to reference nonexisten argument group.'
				)

			else:
				group.add_argument(*args, **kwargs)


	def parse_args(self, args=None, namespace=None):
		"""Wrapper for parse_args method of a parser object. It also
		instantiates action object that will be executed based on a
		input from command line.
		"""

		arguments = self._parsers['main'].parser.parse_args(args, namespace)

		if arguments.usage:
			self._action = _formulate_action(
				ProgramUsageAction,
				parser=self._parsers['main'].parser,
				exitf=self._parsers['main'].parser.exit)

		elif arguments.version:
			self._action = _formulate_action(
				ShowVersionAction,
				prog=self._parsers['main'].parser.prog,
				ver=self.versionString,
				year=self.yearString,
				author=self.authorName,
				license=self.programLicense,
				exitf=self._parsers['main'].parser.exit)

		else:
			self._action = _formulate_action(
				DefaultAction,
				prog=self._parsers['main'].parser.prog,
				exitf=self._parsers['main'].parser.exit)


	def run(self):
		"""This method executes action code.
		"""

		self._action.execute()


#==============================================================================
# App action classes
#==============================================================================

class ProgramAction(object):
	"""Abstract base class for all program actions, that provides execute.

	The execute method contains code that will actually be executed after
	arguments parsing is finished. The method is called from within method
	run of the CommandLineApp instance.
	"""

	def __init__(self, exitf):
		self._exit_app = efitf

	def execute(self):
		pass


class ProgramUsageAction(ProgramAction):
	"""Program action that formats and displays usage message to the stdout.
	"""

	def __init__(self, parser, exitf):
		self._usageMessage = \
		'{usage}Try \'{prog} --help\' for more information.'\
		.format(usage=parser.format_usage(), prog=parser.prog)
		self._exit_app = exitf

	def execute(self):
		print self._usageMessage
		self._exit_app()


class ShowVersionAction(ProgramAction):
	"""Program action that formats and displays program version information
	to the stdout.
	"""

	def __init__(self, prog, ver, year, author, license, exitf):
		self._versionMessage = \
		'{0} {1} Copyright (C) {2} {3}\n{4}'\
		.format(prog, ver, year, author, license)
		self._exit_app = exitf

	def execute(self):
		print self._versionMessage
		self._exit_app()


class DefaultAction(ProgramAction):
	"""Program action that wraps some specific code to be executed based on
	command line input. In this particular case it prints simple message
	to the stdout.
	"""

	def __init__(self, prog, exitf):
		self._programName = prog
		self._exit_app = exitf

	def execute(self):
		print '{0}: Hello World!\n'.format(self._programName)
		self._exit_app()


#==============================================================================
# Script main body
#==============================================================================

if __name__ == '__main__':
	program = CommandLineApp(
		programDescription='Framework for application development \
			implementing argp option parsing engine.\n\n\
			Mandatory arguments to long options are mandatory for \
			short options too.'\
			.replace('\t',''),
		programLicense='License GPLv3+: GNU GPL version 3 or later \
			<http://gnu.org/licenses/gpl.html>\n\
			This is free software: you are free to change and \
			redistribute it.\n\
			There is NO WARRANTY, to the extent permitted by law.'\
			.replace('\t',''),
		versionString='i.i',
		yearString='yyyy',
		authorName='Author Name',
		authorMail='author@mail.com',
		epilog=None)

	program.add_argument_group('general options')
	program.add_argument(
		'-V', '--version',
		action='store_true',
		help='print program version',
		group='general options')
	program.add_argument(
			'--usage',
			action='store_true',
			help='give a short usage message')

	program.parse_args()
	program.run()
