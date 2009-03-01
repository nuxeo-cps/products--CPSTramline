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
# $Id: tramlinefile.py 973 2008-10-20 07:03:15Z joe $

import logging

from OFS.Image import File

from Products.CMFCore.utils import getToolByName

from transactional import get_txn_manager

log = logging.getLogger('Products.CPSTramline.tramlinefile')

class TramlineFile(File):
    """Tramline File object.

    This class is to be used for tramline content only. It's the responsibility
    of the user input stack to instantiate either from this class or from the
    regular Zope File class.
    """

    meta_type = "Tramline File"

    def index_html(self, REQUEST, RESPONSE):
        """Default view method with Tramline headers."""
        RESPONSE.setHeader('tramline_file','')
        # Doesn't make sense to cache at reverse proxy stage, since
        # Apache serves anyway through Tramline. Hence avoid cache pollution.
        # XXX drawback: won't be cached by user agent or in between forward
        # proxies either.
        # We hereby assume that re-requesting attached file content
        # is seldom enough and that proxy admins don't want big files to
        # pollute their cache either.
        RESPONSE.setHeader('Cache-Control','no-store')
	# make range requests reasonible from Zope's point of view
	# XXX ugly hack relying on HTTPRequest's internals
	if REQUEST.get_header('Range'):
	   REQUEST.environ['HTTP_RANGE'] = 'bytes = 0-'
        return File.index_html(self, REQUEST, RESPONSE)


    def getFullFilename(self):
        trtool = getToolByName(self, "portal_tramline", None)
        if trtool is None:
            log.error("Could not find tramline tool.""")
        return trtool.getFilePath(str(self))


    def manage_beforeDelete(self, item, container):
        """Store the path of file to be deleted in repository for commit time.
        """

        path = self.getFullFilename()
        if path:
            get_txn_manager().toDelete(path)

    def manage_afterAdd(self, item, container):
        """Paste part of cut-paste operation."""
        path = self.getFullFilename()
        if path:
            try:
                get_txn_manager().unDelete(path)
            except KeyError:
                pass

    def manage_afterClone(self, item):
        """Clone the tramline file, and register to txn manager for abort."""
        trtool = getToolByName(self, 'portal_tramline')
        # Tool takes care of calling the transaction manager
        # Minor code clarity:
        # Would be more consistent to have the tool return id and path
        # and we'd call the manager from here
        self.update_data(trtool.clone(str(self)))

