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
	"""Abstract base class for _MainProgram and _SubProgram classes.
	
	Every app can be divided into main program and number of subprograms
	(subcommands). This class defines common properties for both types of
	objects.
	"""

	def __init__(self, app):

		# Do some sanity checks first.
		if type(app) is not CommandLineApp:
			raise ValueError('Invalid object type or None.')

		self._app = app
		self._parser = None
		self._argumentGroups = list()


	def _group_by_title(self, title):
		"""It retrieves argument group object from argument groups list for
		given group title. If group with given title does not exist in the
		group list it returns None.
		"""

		group = None

		for item in self._argumentGroups:
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
			
		if type(title) is not str or not title:
			raise ValueError('Empty string or not an string object.')
			

		group = self._parser.add_argument_group(title, description)
		self._argumentGroups.append(group)


	def add_argument(self, *args, **kwargs):
		"""Wrapper for add_argument methods of argparse module. If
		parameter group is supplied with valid group name, argument will
		be added to that group. If group parameter is omitted argument
		will be added to parser object. In a case of invalid group name
		it rises ValueError exception.
		
		Group must be provided as dictionary entru group='groupname'.
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

		# Set default action for the parser.
		self._parser.set_defaults(func=self.formulate_action)


class _MainProgram(_Program):
	"""Class to wrap main parser object, created using argparse.ArgumentParser()
	constructor. It provides an access to basic parser properties, parse_args
	method, as well to subparsers action object.
	
	In a multiparser application there is no need to attach an action factory
	method to the main progarm instance because it will never be called.
	"""

	def __init__(self,
		app=None,
		epilog=None
	):

		_Program.__init__(self, app)

		fmtEpilog = _format_epilog(epilog, self._app.authorMail)

		self._parser = _argparse.ArgumentParser(
			prog = self._app.programName,
			description = self._app.programDescription,
			epilog = fmtEpilog,
			formatter_class = _argparse.RawDescriptionHelpFormatter
			)

		self._subParsers = None


	@property
	def programName(self):
		"""Utility function that makes accessing program name attribute neat
		and hides implementation details.
		"""
		return self._parser.prog


	@property
	def programDescription(self):
		"""Utility function that makes accessing program description attribute
		neat and hides implementation details.
		"""
		return self._parser.description


	def add_subparsers(self, title=None):
		"""Wrapper for add_parsers method of ArgumentParser class. This
		method is provided to enable custom subparsers title setup. If
		'title' parameter is not provided (None) default value is used.
		"""

		if title is not None and type(title) is not str:
			raise ValueError('Invalid parameter type.')
			
		if not title:
			title = \
			'The {0} can be called with following commands'\
			.format(self._parser.prog.strip('.py'))

		self._subParsers = self._parser.add_subparsers(
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
		app=None,
		subParsersObject=None,
		name=None,
		description=None,
		help=None,
		epilog=None
	):

		_Program.__init__(self, app)

		# Do some sanity checks first.
		if not isinstance(subParsersObject, _argparse._SubParsersAction):
			raise ValueError(
				'Subparsers object not initialized or invalid \
				object type.'.replace('\t','')
			)

		if None == name:
			raise NameError('Missing command name.')
			
		if type(name) is not str or not name:
			raise ValueError('Empty string or not an string object.')

		epilogFmtd = _format_epilog(epilog, self._app.authorMail)

		self._parser = subParsersObject.add_parser(
			name,
			description = description,
			epilog = epilogFmtd,
			help = help,
			formatter_class=_argparse.RawDescriptionHelpFormatter
		)


#==============================================================================
# Command line app class
#==============================================================================

class CommandLineApp(object):
	"""Actual command line app object containing all relevant application
	information (NAME, VERSION, DESCRIPTION, ...) and which instantiates through
	attached program objects action that will be executed depending on the user
	input from command line.
	"""

	def __init__(self,
		name=None,
		description=None,
		license=None,
		version=None,
		year=None,
		author=None,
		mail=None
	):
		self._programName = name
		self._programDescription = description
		self._programLicense = license
		self._versionString = version
		self._yearString = year
		self._authorName = author
		self._authorMail = mail
		self._action = None
		self.main = None


	@property
	def programName(self):
		"""Utility function that makes accessing program name attribute neat
		and hides implementation details.
		"""

		# If main program is attached get program name from its property.
		if self.main:
			return self.main.programName
		else:
			return self._programName


	@property
	def programDescription(self):
		"""Utility function that makes accessing program description attribute
		neat and hides implementation details.
		"""

		# If main program is attached get program description from its property.
		if self.main:
			return self.main.programDescription
		else:
			return self._programDescription


	@property
	def programLicense(self):
		"""Provide access to licence text property.
		"""

		return self._programLicense


	@property
	def versionString(self):
		"""Provide access to program's version string property.
		"""

		return self._versionString


	@property
	def yearString(self):
		"""Provide access to program's year string property.
		"""

		return self._yearString


	@property
	def authorName(self):
		"""Provide access to author's name string.
		"""

		return self._authorName


	@property
	def authorMail(self):
		"""Provide access to author's/bug mail string.
		"""

		return self._authorMail


	def attach_program(self, program, obj):
		"""Attach program/subprogram object to application instance. It attach
		program object as named attribute to the app object, setting the name of
		an attribute according to variable 'program'. 'program' variable must be
		nonempty 'string', or else method will rise ValueError. 'obj' must be
		instance of _Program subclass, or else ValueError will be risen.
		"""
	
		# Do some basic sanity checks first.
		if type(program) is not str or not program:
			raise ValueError('Empty string or not an string object.')
		if not issubclass(type(obj), _Program) or type(obj) is _Program:
			raise ValueError('Invalid object type.')

		setattr(self, program, obj)


	def parse_args(self, args=None, namespace=None):
		"""Wrapper for parse_args method of the main program instance.
		"""

		args = self.main.parse_args(args=None, namespace=None)
		self._action = args.func(args)


	def run(self):
		"""Execute proper application action. This method should be called after
		a call to parse_args method.
		"""

		self._action.execute()


#==============================================================================
# Program action classes
#
# ProgramAction class is the abstract base class for all program action classes
# an should not be modified. To define new action class subclass from
# ProgramAction class.
#==============================================================================

class ProgramAction(object):
	"""Abstract base class for all program actions, that provides execute.

	The execute method contains code that will actually be executed after
	arguments parsing is finished. The method is called from within method
	run of the CommandLineApp instance.
	"""

	def __init__(self, exitf):
		self._exit_app = exitf

	def execute(self):
		self._exit_app()


class ShowVersionAction(ProgramAction):
	"""Program action that formats and displays program version information
	to the stdout.
	"""

	def __init__(self, prog, ver, year, author, license, exitf):
		ProgramAction.__init__(self, exitf)
		self._versionMessage = \
		'{0} {1} Copyright (C) {2} {3}\n{4}'\
		.format(prog, ver, year, author, license)

	def execute(self):
		print self._versionMessage
		ProgramAction.execute(self)


class DefaultAction(ProgramAction):
	"""Program action that wraps some specific code to be executed based on
	command line input. In this particular case it prints simple message
	to the stdout.
	"""

	def __init__(self, prog, exitf):
		ProgramAction.__init__(self, exitf)
		self._programName = prog

	def execute(self):
		print '{0}: Hello World!\n'.format(self._programName)
		ProgramAction.execute(self)


#==============================================================================
# Action factories
#
# Action factory methods must accept two arguments, 'obj' holding program object
# to which method is attached and 'args' holding parsed command line arguments.
# When proper program action object is formulated and instantiated, method
# returns this object to the caller.
#==============================================================================

def about_action_factory(obj, args):

	return _formulate_action(
		ShowVersionAction,
		prog=obj._parser.prog,
		ver=obj._app.versionString,
		year=obj._app.yearString,
		author=obj._app.authorName,
		license=obj._app.programLicense,
		exitf=obj._parser.exit,
	)


#==============================================================================
# Script main body
#==============================================================================

if __name__ == '__main__':
	
	# Create an application and feed in relevant application data.
	app = CommandLineApp(
		description='Framework for application development \
			implementing argp option parsing engine.\n\n\
			Mandatory arguments to long options are mandatory for \
			short options too.'\
			.replace('\t',''),
		license='License GPLv3+: GNU GPL version 3 or later \
			<http://gnu.org/licenses/gpl.html>\n\
			This is free software: you are free to change and \
			redistribute it.\n\
			There is NO WARRANTY, to the extent permitted by law.'\
			.replace('\t',''),
		version='i.i',
		year='yyyy',
		author='Author Name',
		mail='author@mail.com'
	)

	# We need at least main program, so let's attach it to our app.
	app.attach_program('main', _MainProgram(app=app, epilog=None))

	# We want for main program to show version info.
	app.main.add_argument(
		'-V', '--version',
		action='version',
		help='print program version',
		version='%(prog)s i.i'
	)
	
	# If we instantiate subprograms (subparsers) we don't need to attach action
	# factory to main program, since that code wil never be executed.

	# We want for our app to have subprograms.
	app.main.add_subparsers()

	# Our only subprogram will show some short application and licence info.
	app.attach_program('about', _SubProgram(
			app=app,
			subParsersObject=app.main.subParsersObject,
			name='about',
			description='Command to print application info to standard output.',
			help='Show application info.',
			epilog=None
		)
	)

	app.about.attach_action_factory(about_action_factory)
	
	# Now we can parse command line arguments.
	app.parse_args()
	
	# Run generated code.
	app.run()