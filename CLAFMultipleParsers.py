#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

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


# ============================================================================
#
# TODO:
#
#
# ============================================================================


# ============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ============================================================================


# =============================================================================
# Modules import section
# =============================================================================

import argparse as _argparse
import types as _types


# =============================================================================
# Global constants
# =============================================================================


#==============================================================================
# Utility classes and functions
#==============================================================================

def _format_epilog(epilog_addition, bug_mail):
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

    fmt_mail = None
    fmt_eplg = None

    if epilog_addition is None and bug_mail is None:
        return None

    if bug_mail is not None:
        fmt_mail = 'Report bugs to <{bug_mail}>.'\
            .format(bug_mail = bug_mail)
    else:
        fmt_mail = None

    if epilog_addition is None:
        fmt_eplg = fmt_mail

    elif fmt_mail is None:
        fmt_eplg = epilog_addition

    else:
        fmt_eplg = '{addition}\n\n{mail}'\
            .format(addition = epilog_addition, mail = fmt_mail)

    return fmt_eplg


def _formulate_action(action, **kwargs):
    """Factory method to create and return proper action object.
    """

    return action(**kwargs)


#==============================================================================
# Program classes
#==============================================================================

class _Program():
    """Abstract base class for _MainProgram and _SubProgram classes.

    Every app can be divided into main program and number of subprograms
    (subcommands). This class defines common properties for both types of
    objects.
    """

    def __init__(self, app_instance):

        # Do some sanity checks first.
        if not isinstance(app_instance, CommandLineApp):
            raise ValueError('Invalid object type or None.')

        self._app_instance = app_instance
        self._parser = None
        self._arg_groups = list()
        self.formulate_action = None


    def _group_by_title(self, title):
        """It retrieves argument group object from argument groups list for
        given group title. If group with given title does not exist in the
        group list it returns None.
        """

        group = None

        for item in self._arg_groups:
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
        if title is None:
            raise NameError('Missing argument group title.')

        if not isinstance(title, str) or not title:
            raise ValueError('Empty string or not an string object.')


        group = self._parser.add_argument_group(title, description)
        self._arg_groups.append(group)


    def add_argument(self, *args, **kwargs):
        """Wrapper for add_argument methods of argparse module. If
        parameter group is supplied with valid group name, argument will
        be added to that group. If group parameter is omitted argument
        will be added to parser object. In a case of invalid group name
        it rises ValueError exception.

        Group must be provided as dictionary entru group='groupname'.
        """

        group = kwargs.pop('group', None)

        if group is None:
            self._parser.add_argument(*args, **kwargs)

        else:
            gobj = self._group_by_title(group)

            if gobj is None:
                raise ValueError(
                    'Trying to reference nonexisten \
                    argument group.'.replace('\t','')
                )

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
        app_instance=None,
        epilog=None
    ):

        _Program.__init__(self, app_instance)

        fmt_epilog = _format_epilog(epilog, self._app_instance.author_mail)

        self._parser = _argparse.ArgumentParser(
            prog = self._app_instance.program_name,
            description = self._app_instance.program_description,
            epilog = fmt_epilog,
            formatter_class = _argparse.RawDescriptionHelpFormatter
            )

        self._sub_parsers = None


    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute neat
        and hides implementation details.
        """
        return self._parser.prog


    @property
    def program_description(self):
        """Utility function that makes accessing program description attribute
        neat and hides implementation details.
        """
        return self._parser.description


    def add_subparsers(self, title=None):
        """Wrapper for add_parsers method of ArgumentParser class. This
        method is provided to enable custom subparsers title setup. If
        'title' parameter is not provided (None) default value is used.
        """

        if not isinstance(title, str):
            raise ValueError('Invalid parameter type.')

        if not title:
            title = \
            'The {0} can be called with following commands'\
            .format(self._parser.prog.strip('.py'))

        self._sub_parsers = self._parser.add_subparsers(
            title=title,
            dest='command',
            metavar=''
        )


    @property
    def sub_parsers_object(self):
        """Provides access to subparsers object which have to be provided when
        instantiating subprogram objects.
        """

        return self._sub_parsers


    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of the parser object.
        """

        return self._parser.parse_args(args, namespace)


class _SubProgram(_Program):
    """Class to wrap subparser objects, created using
    _subParsersAction.ArgumentParser() constructor.
    """

    def __init__(self,
        app_instance=None,
        sub_parsers_object=None,
        name=None,
        description=None,
        help=None,
        epilog=None
    ):

        _Program.__init__(self, app_instance)

        # Do some sanity checks first.
        if not isinstance(sub_parsers_object, _argparse._SubParsersAction):
            raise ValueError(
                'Subparsers object not initialized or invalid \
                object type.'.replace('\t','')
            )

        if name is None:
            raise NameError('Missing command name.')

        if not isinstance(name, str) or not name:
            raise ValueError('Empty string or not an string object.')

        fmtd_eplg = _format_epilog(epilog, self._app_instance.author_mail)

        self._parser = sub_parsers_object.add_parser(
            name,
            description = description,
            epilog = fmtd_eplg,
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
        self._program_name = name
        self._program_description = description
        self._program_license = license
        self._version_string = version
        self._year_string = year
        self._author_name = author
        self._author_mail = mail
        self._action = None
        self.main = None


    @property
    def program_name(self):
        """Utility function that makes accessing program name attribute neat
        and hides implementation details.
        """

        # If main program is attached get program name from its property.
        if self.main:
            return self.main.program_name

        return self._program_name


    @property
    def program_description(self):
        """Utility function that makes accessing program description attribute
        neat and hides implementation details.
        """

        # If main program is attached get program description from its property.
        if self.main:
            return self.main.program_description

        return self._program_description


    @property
    def program_license(self):
        """Provide access to licence text property.
        """

        return self._program_license


    @property
    def version_string(self):
        """Provide access to program's version string property.
        """

        return self._version_string


    @property
    def year_string(self):
        """Provide access to program's year string property.
        """

        return self._year_string


    @property
    def author_name(self):
        """Provide access to author's name string.
        """

        return self._author_name


    @property
    def author_mail(self):
        """Provide access to author's/bug mail string.
        """

        return self._author_mail


    def attach_program(self, program, obj):
        """Attach program/subprogram object to application instance. It attach
        program object as named attribute to the app object, setting the name of
        an attribute according to variable 'program'. 'program' variable must be
        nonempty 'string', or else method will rise ValueError. 'obj' must be
        instance of _Program subclass, or else ValueError will be risen.
        """

        # Do some basic sanity checks first.
        if not isinstance(program, str) or not program:
            raise ValueError('Empty string or not an string object.')
        if not issubclass(type(obj), _Program)\
                or not isinstance(obj, _Program):
            raise ValueError('Invalid object type.')

        setattr(self, program, obj)


    def parse_args(self, args=None, namespace=None):
        """Wrapper for parse_args method of the main program instance.
        """

        args = self.main.parse_args(args, namespace)
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

class ProgramAction():
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        self._exit_app()


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def __init__(self, prog, ver, year, author, license, exitf):
        super().__init__(exitf)
        self._version_message = '{0} {1} Copyright (C) {2} {3}\n{4}'\
                .format(prog, ver, year, author, license)

    def execute(self):
        print(self._version_message)
        super().execute()


class DefaultAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    def __init__(self, prog, exitf):
        super().__init__(exitf)
        self._program_name = prog

    def execute(self):
        print('{0}: Hello World!\n'.format(self._program_name))
        super().execute()


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
    app.attach_program('main', _MainProgram(app_instance=app, epilog=None))

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
            app_instance=app,
            sub_parsers_object=app.main.sub_parsers_object,
            name='about',
            description='Command to print application info to standard output.',
            help='Show application info.',
            epilog=None
        )
    )

    # Now we can parse command line arguments.
    app.parse_args()

    # Run generated code.
    app.run()
