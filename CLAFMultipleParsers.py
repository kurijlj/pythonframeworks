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


import argparse as _argparse
import types as _types


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


def _attach_action_factory(target, method):
	"""
	def action_factory(obj, args):
		return ActionObject
	"""

	target.method = _types.MethodType(method, target)


#==============================================================================
# Program classes
#==============================================================================

class _Program(object):
	"""Abstract base class for _MainProgram and _SubProgram classes.
	
	Every app can be divided into main program and number of subprograms
	(subcommands). This class defines common properties for both types of
	objects.
	"""

	def __init__(self):
		self._parser.set_defaults(func=self.formulate_action)
		self._argumentGroups = list()


	def _group_by_title(self, title):
		"""It retrieves argument group object from argument groups list for
		given group title. If group with given title does not exist in the
		group list it returns None.
		"""

		group = None

		for item in p._argumentGroups:
			if title == item.title:
				group = item
				break

		return group


	def add_argument_group(self, title=None, description=None):
		"""Adds an argument group to the program object.
		At least group title must be provided or method will rise
		NameError exception. This is to prevent creation of titleless
		and descriptionless argument groups. Although this is allowed by
		argparse module I don't see any use of a such utility."""

		# Do some sanity checks first.
		if None == title:
			raise NameError('Missing argument group title.')

		group = self._parser.add_argument_group(title, description)
		self._argumentGroups.append(group)


	def add_argument(self, *args, **kwargs):
		"""Wrapper for add_argument methods of argparse module. If
		parameter group is supplied with valid group name, argument will
		be added to that group. If group parameter is omitted argument
		will be added to parser object. In a case of invalid group name
		it rises ValueError exception.
		"""

		group = kwargs.pop('group', None)

		if None == group:
			self._parser.add_argument(*args, **kwargs)

		else:
			gobj = self._group_by_title(group)

			if None == gobj:
				raise ValueError(
					'Trying to reference nonexisten \
					argument group.'.replace('\t','')
				)

			else:
				gobj.add_argument(*args, **kwargs)


	def attach_action_factory(self, method):
		"""Attach action factory method to the program object.
		
		Action factory method is used to formulate proper action (program action
		object) according to user given command line options.
		
		Action factory method is to be defined outside program object. It must
		accept two arguments, 'obj' holding program object to which method
		is attached and 'args' holding parsed command line arguments. When
		proper program action object is formulated and instantiated, method
		returns this object to the caller.
		"""
	
		self.formulate_action = _types.MethodType(method, self)



class _MainProgram(_Program):
	"""Class to wrap main parser object, created using argparse.ArgumentParser()
	constructor. It also provides an access to basic parser properties, as well
	as parse_args method.
	"""

	def __init__(self,
		name=None,
		description=None,
		epilog=None,
		mail=None
	):

		fmtEpilog = _format_epilog(epilog, mail)

		self._parser = _argparse.ArgumentParser(
			prog = name,
			description = description,
			epilog = epilog,
			formatter_class = _argparse.RawDescriptionHelpFormatter
			)

		_Program.__init__(self)

		self._subParsers = None


	@property
	def programName(self):
		"""Utility function that makes accessing program name attribute
		neat and hides implementation details.
		"""
		return self._parser.prog


	@property
	def programDescription(self):
		"""Utility function that makes accessing program description
		attribute neat and hides implementation details.
		"""
		return self._parser.description


	def add_subparsers(self, title=None):
		"""Wrapper for add_parsers method of ArgumentParser class. This
		method is provided to enable custom subparsers title setup. If
		'title' parameter is not provided (None) default value is used.
		"""

		if None == title:
			title = \
			'The {0} can be called with following commands:'\
			.format(self._parser.prog.strip('.py'))

		self._subParsers = self._parser.add_parsers(
			title=title,
			dest='command',
			metavar=''
		)


	@property
	def subParsersObject(self):
		"""Provides access to subparsers object which have to be provided when
		instantiating subprogram objects.
		"""

		return self._subParsers


	def parse_args(self, args=None, namespace=None):
		"""Wrapper for parse_args method of the parser object.
		"""

		return self._parser.parse_args(args, namespace)


class _SubProgram(_Program):
	"""Class to wrap subparser objects, created using
	_subParsersAction.ArgumentParser() constructor.
	"""

	def __init__(self,
		subParsersObject=None,
		name=None,
		description=None,
		epilog=None,
		help=None
	):

		# Do some sanity checks first.
		if not isinstance(subParsersObject, _argparse._SubParsersAction):
			raise ValueError(
				'Subparsers object not initialized or invalid \
				object type.'.replace('\t','')
		)

		if None == commandName:
			raise NameError('Missing command name.')

		epilogFmtd = _format_epilog(commandEpilog, self.authorMail)

		self._parser = subParsersObject.add_parser(
			name,
			description = description,
			epilog = epilogFmtd,
			help = help,
			formatter_class=_argparse.RawDescriptionHelpFormatter
		)

		_Program.__init__(self)



#==============================================================================
# Command line app class
#==============================================================================

class CommandLineApp(object):
	"""Actual command line app object containing all relevant application
	information (NAME, VERSION, DESCRIPTION, ...) and which instantiates
	action that will be executed depending on the user input from
	command line.
	"""

	def __init__(self):
		pass


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
	#program = CommandLineApp(
	#	programDescription='Framework for application development \
	#		implementing argp option parsing engine.\n\n\
	#		Mandatory arguments to long options are mandatory for \
	#		short options too.'\
	#		.replace('\t',''),
	#	programLicense='License GPLv3+: GNU GPL version 3 or later \
	#		<http://gnu.org/licenses/gpl.html>\n\
	#		This is free software: you are free to change and \
	#		redistribute it.\n\
	#		There is NO WARRANTY, to the extent permitted by law.'\
	#		.replace('\t',''),
	#	versionString='i.i',
	#	yearString='yyyy',
	#	authorName='Author Name',
	#	authorMail='author@mail.com',
	#	epilog=None)
	#
	#program.add_argument_group('general options')
	#program.add_argument(
	#	'-V', '--version',
	#	action='store_true',
	#	help='print program version',
	#	group='general options')
	#program.add_argument(
	#		'--usage',
	#		action='store_true',
	#		help='give a short usage message')
	#
	#program.parse_args()
	#program.run()
	mainprg = _MainProgram(
		name=None,
		description='This is main program.',
		epilog=None,
		mail='kurijlj@gmail.com'
	)
