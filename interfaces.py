# (C) Copyright 2008 Tonal
# Author: Georges Racinet <georges@racinet.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: interfaces.py 973 2008-10-20 07:03:15Z joe $

from zope.interface import Interface

class ITramlineTool(Interface):
    """Tramline tool.
    """
    def getFilePath(tramid):
        """Return the path on FS for tramline file with given id."""

    def remove(tramid):
        """Remove file with given id.

        Implementation may either remove permanently or move to a trash area."""
