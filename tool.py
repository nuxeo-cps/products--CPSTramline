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

import logging
import os
import errno
import sys
import random
from tempfile import mkstemp

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from zope.interface import implements

from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject

from tramlinepath import id_to_path
from tramlinefile import TramlineFile
from tramlinefile import OLD_TITLE_ATTR

from transactional import get_txn_manager

from interfaces import ITramlineTool

HR_AREA = "human_readable"

logger = logging.getLogger('Products.CPSTramline.tool')

def make_path_relative(ref, target):
    """Makes the absolute target path relative to ref.

    Intended for use to make symlinks relative, so that moving the repository
    is possible.

    >>> parent_dir = os.path.pardir
    >>> ref = os.path.join('x', 'y', 't') # x/y/t
    >>> make_path_relative(ref, os.path.join('x', 'y', 'z')) # x/y/z
    'z'
    >>> expected = os.path.join(parent_dir, 'a') # ../a
    >>> make_path_relative(ref, os.path.join('x', 'a')) == expected
    True
    """

    parent_dir = os.path.pardir
    sep = os.path.sep
    res = []
    while True:
        ref = os.path.split(ref)[0]
        if target.startswith(ref):
            break
        res.append(parent_dir)
    res.append(target[len(ref)+len(sep):])
    return os.path.join(*res)

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

    def getHumanReadablePath(self, tramid, filename):
        """Return a human readable path for the given tramline ids and filename
        Designed so that uniqueness issues are logically equivalent to those
        of tramid

        The current implementation will make this a symlink
        >>> tool = TramlineTool()
        >>> tool.tramlinepath = '/base/path'
        >>> tool.relative = False
        >>> tool.getHumanReadablePath('some_id', 'file_with_no_extension')
        '/base/path/human_readable/file_with_no_extension-some_id'
        >>> tool.getHumanReadablePath('some_id', 'report.pdf')
        '/base/path/human_readable/report-some_id.pdf'

        Behaviour with multiple dots
        >>> tool.getHumanReadablePath('31459', 'manual-4-283587865.1-en.a4.pdf')
        '/base/path/human_readable/manual-4-283587865.1-en.a4-31459.pdf'
        """
        base = self.getTramlinePath()
        split = filename.rsplit('.', 1)
        if len(split) == 1:
            filename = '-'.join((filename, tramid))
        else:
            filename = '%s-%s.%s' % (split[0], tramid, split[1])
        return os.path.join(os.path.join(base, HR_AREA, filename))

    security.declarePrivate('makeSymlink')
    def makeSymlink(self, path, tramid, filename, may_exist=True):
        """Create a human readable, relative, symlink for the given tramid.

        path is the path to the file in the repository
        filename is the original posted attachment name (would also be the
        title of the File object)

        Takes care of transactional aspects and returns the absolute path
        of the symlink.

        if may_exist is True, there won't be any error if the link is already
        there; instead, nothing happens.
        """
        newhrpath = self.getHumanReadablePath(tramid, filename)
        base_dir = os.path.split(newhrpath)[0]
        if not os.path.exists(base_dir):
            os.mkdir(base_dir) # XXX make equivalent of mkdir -p eventually

        if may_exist:
            if os.path.islink(newhrpath):
                logger.info("Symbolic link already exists : %s", newhrpath)
                return newhrpath
        os.symlink(make_path_relative(newhrpath, path), newhrpath)

        tm = get_txn_manager()
        tm.created(newhrpath)
        # in case prior processing asked for deletion, cancel it
        # can happen with some in-place modifications
        tm.unDelete(newhrpath)
        return newhrpath

    security.declarePrivate('makeSymlinkFor')
    def makeSymlinkFor(self, fobj, may_exist=True):
        """Same as makeSymlink, for a Tramline File object."""
        assert(isinstance(fobj, TramlineFile))
        self.cleanOldSymlinkFor(fobj)
        return self.makeSymlink(fobj.getFullFilename(), str(fobj), fobj.title,
                                may_exist=may_exist)

    def cleanOldSymlinkFor(self, fobj):
        """Remove any symlink related to a prior filename"""
        assert(isinstance(fobj, TramlineFile))
        fobj = fobj.aq_base
        old = getattr(fobj, OLD_TITLE_ATTR, None)
        if not old:
            return

        get_txn_manager().toDelete( self.getHumanReadablePath(str(fobj), old))
        delattr(fobj, OLD_TITLE_ATTR)

    security.declarePrivate('_link')
    def _link(self, path):
        """Make a guaranteed new (hard) link in repo for file at path.

        Return tramid, newpath
        """
        while True:
            newid = str(random.randrange(sys.maxint))
            newpath = self.getFilePath(newid)

            if os.path.exists(newpath):
                continue
            try:
                os.link(path, newpath)
            except os.error, e:
                if e.errno == errno.EEXIST:
                    continue # one more time
                raise
            return newid, newpath

    security.declarePrivate('getFilePath')
    def clone(self, tramid, filename):
        """Clone the file in repository with given id.

        This is done by a hard link, so that
          - it's cheap,
          - one can be deleted without impact on the other,
          - we get a gc for free thanks to the os.

        filename is been used to create the human-readable symbolic link
        """
        newid, newpath = self._link(self.getFilePath(tramid))
        self.makeSymlink(newpath, newid, filename)
        get_txn_manager().created(newpath)
        return newid

    security.declarePrivate('finalizeIdUpdate')
    def finalizeIdUpdate(self, fobj, old_id):
        """Remove references to old_id to replace them by new_id.

        This is useful in case of PUT (ExternalEditor)"""

        tm = get_txn_manager()
        tm.toDelete(self.getHumanReadablePath(old_id, fobj.title))
        tm.toDelete(self.getFilePath(old_id))
        self.makeSymlink(fobj.getFullFilename(), str(fobj), fobj.title)

    security.declarePrivate('create')
    def create(self, filename, data):
        """Create a file in the repository from raw data.
        Return tramline id, actual size as observed on fs

        Returning the size will be important if data can be a stream,
        which is not currently the case.
        """

        # Dumping in 2 steps to avoid race condition on tramline ids
        fd, tmppath = mkstemp(dir=self.getTramlinePath())
        f = os.fdopen(fd, 'w')
        if isinstance(data, str):
            f.write(data)
        else: # file-like object
            data.seek(0L)
            while True:
                chunk = data.read(65536)
                if not chunk:
                    break
                f.write(chunk)

        f.close()

        newid, newpath = self._link(tmppath)
        os.chmod(tmppath, 0660)
        os.unlink(tmppath)

        get_txn_manager().created(newpath)
        self.makeSymlink(newpath, newid, filename)

        return newid, os.path.getsize(newpath)

InitializeClass(TramlineTool)
