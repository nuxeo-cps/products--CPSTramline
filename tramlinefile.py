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

import logging
import os

try:
    import PIL.Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

import OFS.Image
from OFS.Image import Image, File
from Products.CMFCore.utils import getToolByName

from transactional import get_txn_manager

log = logging.getLogger(__name__)

OLD_TITLE_ATTR = '_v_old_title'

class TramlineFile(File):
    """Tramline File object.

    This class is to be used for tramline content only. It's the responsibility
    of the user input stack to instantiate either from this class or from the
    regular Zope File class.
    """

    meta_type = "Tramline File"

    OFSClass = File

    def __init__(self, *args, **kwargs):
        """kwargs:
           actual_size to specify from the start.
           creation_context: useful before object is persisted."""

        actual_size = kwargs.pop('actual_size', None)
        creation_context = kwargs.pop('creation_context', None)
        if creation_context is not None:
            self._v_creation_context = creation_context
        File.__init__(self, *args, **kwargs)
        self.actual_size = actual_size

    def index_html(self, REQUEST, RESPONSE):
        """Default view method with Tramline headers."""
        RESPONSE.setHeader('tramline_file', '')
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

    def PUT(self, REQUEST, RESPONSE):
        old_id = str(self)
        File.PUT(self, REQUEST, RESPONSE)
        self.data = str(self).strip() # tramline has a hard time avoiding \r\n
        RESPONSE.setHeader('tramline_ok', '')
        trtool = getToolByName(self, 'portal_tramline')
        trtool.finalizeIdUpdate(self, old_id)

    def manage_FTPget(self, *args, **kwargs):
        """Used by ExternalEditor to encapsulate content with its headers."""

        try:
            resp = self.REQUEST.RESPONSE
        except AttributeError:
            pass
        else:
            resp.setHeader("tramline_file", '')

        return File.manage_FTPget(self, *args, **kwargs)

    def get_size(self):
        """User level size."""

        size = getattr(self, 'actual_size', None)
        if size:
            return size

        path = self.getFullFilename(allow_tmp=True)
        if path is None:
            # tool not available yet. A later call will do it
            return 0

        try:
            size = self.actual_size = os.path.getsize(path)
        except os.error:
            log.error(
                "OS error while trying to retrieve size of tramline file '%s'",
                path)
            return 0

        return size

    # deprecated, use get_size
    getSize = get_size

    def getFullFilename(self, allow_tmp=False):
        trtool = getToolByName(self, "portal_tramline", None)
        if trtool is None:
            context = getattr(self, '_v_creation_context', None)
            if context is not None:
                trtool = getToolByName(context, 'portal_tramline', None)

        if trtool is None:
            log.error("Could not find tramline tool.""")
            return
        return trtool.getFilePath(str(self), allow_tmp=allow_tmp)

    def getFileHandler(self):
        """Return an open file for the actual filesystem content."""
        path = self.getFullFilename(allow_tmp=True)
        if path is None:
            # tool not available yet (aq problem). Can't proceed
            raise RuntimeError("Tramline tool not available")

        return open(path) # no exc catching is better here

    def getHumanReadablePath(self):
        """Return the symbolic link path.
        """
        trtool = getToolByName(self, "portal_tramline", None)
        if trtool is None:
            log.error("Could not find tramline tool.""")

        return trtool.getHumanReadablePath(str(self), self.title)

    def manage_beforeDelete(self, item, container):
        """Store the path of file to be deleted in repository for commit time.
        """

        # just in case
        getToolByName(self, 'portal_tramline').cleanOldSymlinkFor(self)

        path = self.getFullFilename()
        if path:
            mgr = get_txn_manager()
            mgr.toDelete(path)
            hr_path = self.getHumanReadablePath()
            mgr.toDelete(hr_path)

    def __setattr__(self, k, v):
        old = self.__dict__.get(k)
        File.__setattr__(self, k, v)
        if k == 'title':
            # XXX hack because we don't have aq context here to get the tool
            # this will be cleaned later on (if change is made
            # through DataModel, this File will be removed and added back)
            File.__setattr__(self, OLD_TITLE_ATTR, old)

    def manage_afterAdd(self, item, container):
        """Paste part of cut-paste operation."""
        path = self.getFullFilename()
        trtool = getToolByName(self, 'portal_tramline')
        # in case this is called from a DataModel commit without any change,
        # the link already exists. This happens, e.g. in call to
        # CPSDocument.edit() from CPSCore.ProxyBase.FileDownloader.PUT()
        hr_path = trtool.makeSymlinkFor(self, may_exist=True)

        if path:
            try:
                manager = get_txn_manager()
                manager.unDelete(path, hr_path)
            except KeyError:
                pass

    def manage_afterClone(self, item):
        """Clone the tramline file, and register to txn manager for abort."""
        trtool = getToolByName(self, 'portal_tramline')
        trtool.cleanOldSymlinkFor(self)
        # Tool takes care of calling the transaction manager
        # Minor code clarity:
        # Would be more consistent to have the tool return id and path
        # and we'd call the manager from here
        self.update_data(trtool.clone(str(self), self.title))

    @classmethod
    def create(self, oid, title, data, context=None, size_threshold=0, **kw):
        """Create either TramlineFile or File according to threshold.

        context is mandatory (kwarg for upstream code clarity/ease only)
        The actual file in tramline repository is also created.
        The size treshold avoids littering the repository with tiny files.
        """

        if context is None:
            # even if we end up creating an OFS File this time, this is a fault
            raise ValueError("Need context")

        trtool = getToolByName(context, 'portal_tramline', None)
        if isinstance(data, file):
            try:
                data.seek(0, 2) # os.SEEK_END not available in python 2.4
                size = data.tell()
                data.seek(0)
            except OSError: # not much can be done for special files
                size = 0
        else:
            size = len(data)
        # trtool being None means that tramline is not installed !
        # a contrario, if tramlinetool is there, all automatic content
        # (see #2205) must be tramline capable (ie use tramline aware widgets)
        if trtool is None or size_threshold > size:
            return self.OFSClass(oid, title, data)

        tramid, size = trtool.create(title, data)
        return self(oid, title, tramid, actual_size=size, creation_context=context, **kw)

class TramlineImage(TramlineFile, Image):

    meta_type = 'Tramline Image'

    OFSClass = Image

    # private
    update_data__roles__=()
    def update_data(self, data, content_type=None, size=None):
        """As OFS.Image, this extracts content type, height and weight

        Differences: knows that data is just the tramid,
        The passed size are for File objects and is the tramid length
        if and only if getActualSize does not work.
        """
        File.update_data(self, data, content_type=content_type, size=size)

        f = self.getFileHandler()
        ct, width, height = getImageInfoFromFile(f)
        f.close() # never hurts
        if ct:
            content_type = ct
        if width >= 0 and height >= 0:
            self.width = width
            self.height = height

        # Now we should have the correct content type, or still None
        if content_type is not None: self.content_type = content_type

        self.ZCacheable_invalidate()
        self.ZCacheable_set(None)
        self.http__refreshEtag()

def getImageInfoFromFile(f):
    """Same as OFS.Image, working on a python file object.

    Leverages the stronger PIL if available.
    Remark: OFS.Image.File does not load all of the image in RAM for that
    purpose (self.data is just the first chunk, that's 2^16, still a lot).
    """
    if PIL_OK:
        img = PIL.Image.open(f)
        return ('image/' + img.format.lower(), ) + img.size

    data = f.read(24) # Same length as ImageWidget uses
    return OFS.Image.getImageInfo(data)
