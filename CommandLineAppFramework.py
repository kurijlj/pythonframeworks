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

class ProgramAction:
	"""Abstract base class for all program actions, that provides execute.

	The execute method contains code that will actually be executed after
	arguments parsing is finished. The method is called from within method
	run of the CommandLineApp instance.
	"""

	def execute(self):
		pass


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


class CommandLineApp:
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

		self._parser = argparse.ArgumentParser(
			prog = programName,
			description = programDescription,
			epilog = fmtEpilog,
			formatter_class=argparse.RawDescriptionHelpFormatter
			)

		# Since we add argument options to groups by calling group
		# method add_argument, we have to sore all that group objects
		# somewhere before adding arguments. Since we want to store all
		# application relevant data in our application object we use
		# this list for that purpose.
		self._argumentGroups = []


	def programName(self):
		"""Utility function that makes accessing program name attribute
		neat and hides implementation details.
		"""
		return self._parser.prog


	def programDescription(self):
		"""Utility function that makes accessing program description
		attribute neat and hides implementation details.
		"""
		return self._parser.description


	def add_argument_group(self, title=None, description=None):
		"""Adds an argument group to application object.
		At least group title must be provided or method will rise
		NameError exception. This is to prevent creation of titleless
		and descriptionless argument groups. Although this is allowed bu
		argparse module I don't see any use of a such utility."""

		if None == title:
			raise NameError('Missing arguments group title.')

		group = self._parser.add_argument_group(title, description)
		self._argumentGroups.append(group)

		return group


	def _group_by_title(self, title):
		group = None

		for item in self._argumentGroups:
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

		if 'group' not in kwargs or None == kwargs['group']:
			self._parser.add_argument(*args, **kwargs)

		else:
			group = self._group_by_title(kwargs['group'])

			if None == group:
				raise ValueError(
				'Trying to reference nonexisten argument group.'
				)

			else:
				kwargsr = {k:kwargs[k] for k in kwargs.keys() \
					if 'group' != k}
				group.add_argument( *args, **kwargsr)


	def parse_args(self, args=None, namespace=None):
		"""Wrapper for parse_args method of a parser object. It also
		instantiates action object that will be executed based on a
		input from command line.
		"""

		arguments = self._parser.parse_args(args, namespace)

		if arguments.usage:
			self._action = ProgramUsageAction(self._parser)

		elif arguments.version:
			self._action = ShowVersionAction(
				self.programName(),
				self.versionString,
				self.yearString,
				self.authorName,
				self.programLicense)

		else:
			self._action = DefaultAction(self.programName())


	def run(self):
		"""This method executes action code and terminates application.
		"""

		self._action.execute()
		self._parser.exit()


class ProgramUsageAction(ProgramAction):
	"""Program action that formats and displays usage message to the stdout.
	"""
	
	def __init__(self, parser):
		self._usageMessage = \
		'{usage}Try \'{prog} --help\' for more information.'\
		.format(usage=parser.format_usage(), prog=parser.prog)
	
	def execute(self):
		print self._usageMessage
	
	
class ShowVersionAction(ProgramAction):
	"""Program action that formats and displays program version information
	to the stdout.
	"""
	
	def __init__(self, prog, ver, year, author, license):
		self._versionMessage = \
		'{0} {1} Copyright (C) {2} {3}\n{4}'\
		.format(prog, ver, year, author, license)
	
	def execute(self):
		print self._versionMessage
	
	
class DefaultAction(ProgramAction):
	"""Program action that wraps some specific code to be executed based on
	command line input. In this particular case it prints simple message
	to the stdout.
	"""

	def __init__(self, prog):
		self._programName = prog

	def execute(self):
		print '{0}: Hello World!\n'.format(self._programName)


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
