#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of versiontools.
#
# versiontools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# versiontools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with versiontools.  If not, see <http://www.gnu.org/licenses/>.

"""
Versiontools help build useful __version__ objects for your projects
"""

import os
import operator

class Version(tuple):
    """
    Version object suitable to be placed in module's __version__

    Version class is a tuple and has the same logical components as
    :data:`sys.version_info`.


    It has some extra abilities in the way __str__ is implemented and in
    the way the constructor can find the revision number of a version
    control system and use it in place of serial number when it is not
    specified. This second feature is only enabled when the releaselevel
    is set to the string "dev"

    .. note::
        Currently to use vcs integration you *must* use the name
        __version__ in your variable name and you *must* define it at
        module level.  There is some fuzzy logic that walks the
        traceback looking for '__version__'.
    """

    def __new__(cls, major, minor, micro=0, releaselevel="dev", serial=None):
        assert releaselevel in ('dev', 'alpha', 'beta', 'candidate', 'final')
        if releaselevel == "dev" and serial is None:
            serial = cls._query_vcs()
        if serial is None:
            serial = 0
        return tuple.__new__(cls, (major, minor, micro, releaselevel, serial))

    major = property(operator.itemgetter(0))
    minor = property(operator.itemgetter(1))
    micro = property(operator.itemgetter(2))
    releaselevel = property(operator.itemgetter(3))
    serial = property(operator.itemgetter(4))

    @classmethod
    def _find_source_tree(cls):
        """
        Find the absolute pathname of the tree that contained the file
        that called our __init__()
        """
        import inspect
        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        for index0, record in enumerate(outer_frames):
            frame, filename, lineno, func_name, context, context_index = record
            if func_name == "<module>" and "__version__" in context[context_index]:
                caller = frame
                break
        else:
            caller = None
        if caller:
            return os.path.dirname(os.path.abspath((inspect.getsourcefile(caller))))

    @classmethod
    def _query_vcs(cls):
        """
        Query version control system for the value of serial number.
        The actual version control integration is pluggable, anything
        that provides an entrypoint for versintools.vcs_integration" is
        considered. The first version control system that finds the
        revision number wins.
        """
        import pkg_resources
        source_tree = cls._find_source_tree()
        if source_tree is None:
            return
        for entrypoint in pkg_resources.iter_entry_points("versiontools.vcs_integration"):
            integration_cls = entrypoint.load()
            integration = integration_cls.from_source_tree(source_tree)
            if integration:
                return integration.revno

    def __str__(self):
        """
        Return a string representing the version of this package

        The string is not a direct concatenation of all version
        components.  Instead it's a more natural 'human friendly'
        version where components with certain values are left out.
        """
        version = "%s.%s" % (self.major, self.minor)
        if self.micro != 0:
            version += ".%s" % self.micro
        if self.releaselevel != 'final':
            version += ".%s" % self.releaselevel
        if self.releaselevel != 'final' and self.serial:
            version += '.%s' % self.serial
        return version


__version__ = Version(1, 0, 2, "dev")
