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
# $Id: tool.py 973 2008-10-20 07:03:15Z joe $

import os
import errno
import sys
import random

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from zope.interface import implements

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from tramline.core import id_to_path

from transactional import get_txn_manager

from interfaces import ITramlineTool

class TramlineTool(UniqueObject, SimpleItemWithProperties):
    id = 'portal_tramline'
    meta_type = 'Tramline Tool'

    implements(ITramlineTool)

    _properties=(
            {'id':'tramlinepath', 'type':'string', 'mode':'w'},
            {'id':'relative', 'type':'boolean', 'mode':'w',
             'label': 'Is the path relative to CLIENT_HOME?'},
            )
    tramlinepath = "tramline_files"
    relative = True

    security = ClassSecurityInfo()

    manage_options = SimpleItemWithProperties.manage_options + (
        {'label': 'Export',
         'action': 'manage_genericSetupExport.html',
         },
        )

    security.declarePrivate('getTramlinePath')
    def getTramlinePath(self):
        p = self.getProperty('tramlinepath')
        if self.relative:
            return os.path.join(CLIENT_HOME, p)

        return p

    security.declarePrivate('getFilePath')
    def getFilePath(self, tramid, allow_tmp=False):
        """Return the path on FS for tramline file with given id.

        The file is *never* guaranteed to exist, however if allow_tmp is True
        and the file is not found in repository, then a path from tramline
        temporary directory is returned.

        This both relies on and insulates tramline implementation details."""

        base = self.getTramlinePath()

        path = id_to_path(base, tramid, create_intermediate=True)
        if not allow_tmp:
            return path

        if not os.path.isfile(path):
            path = id_to_path(base, tramid, 
	                      create_intermediate=True, upload=True)

        return path

    security.declarePrivate('getFilePath')
    def clone(self, tramid):
        """Clone the file in repository with given id.

        This is done by a hard link, so that
          - it's cheap,
          - one can be deleted without impact on the other
          - we get a gc for free thanks to the os.
        """
        while True:
            newid = str(random.randrange(sys.maxint))
            newpath = self.getFilePath(newid)

            if os.path.exists(newpath):
                continue
            try:
                os.link(self.getFilePath(tramid), newpath)
            except os.error, e:
                if e.errno == errno.EEXIST:
                    continue # one more time
                raise
            break
        get_txn_manager().created(newpath)
        return newid

InitializeClass(TramlineTool)
