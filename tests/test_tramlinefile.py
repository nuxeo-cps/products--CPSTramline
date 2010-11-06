# (C) Copyright 2009 Georges Racinet
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
# $Id$

import unittest
from tramlinetestcase import CPSTramlineTestCase

import os
import tempfile
from OFS.Image import File
from Products.CPSTramline.tramlinefile import TramlineFile, TramlineImage

class TramlineFileTestCase(CPSTramlineTestCase):

    def afterSetUp(self):
        CPSTramlineTestCase.afterSetUp(self)

        ttool = self.ttool = self.portal.portal_tramline

        self.login('manager')
        wftool = self.portal.portal_workflow
        wftool.invokeFactoryFor(self.portal.workspaces, 'File', 'the_file')
        fproxy = self.portal.workspaces.the_file
        dm = fproxy.getContent().getDataModel(proxy=fproxy)
        dm['file'] = tramfile = TramlineFile('file', 'report.pdf',
                                             'some_tramid',
                                             actual_size=17L,
                                             creation_context=fproxy)
        # simulate creation of file by tramline within Apache server
        fd = open(tramfile.getFullFilename(), 'w')
        fd.write('a' * 17)
        fd.close()

        dm._commit()
        self.fproxy = self.portal.workspaces.the_file
        self.tramfile = self.fproxy.getContent().file
        self.ttool = self.portal.portal_tramline

    def testCreation(self):
        ttool = self.portal.portal_tramline
        fobj = self.tramfile
        lnpath = ttool.getHumanReadablePath(str(fobj), fobj.title)
        self.assertTrue(os.path.islink(lnpath))
        realpath = os.path.realpath
        self.assertEquals(realpath(lnpath), realpath(fobj.getFullFilename()))

        # In real life, often that the symlink creation hook is called twice
        # Test that it reacts properly
        ttool.makeSymlinkFor(fobj)

    def testCreateClassMethod(self):
        # From str, too small
        tf = TramlineFile.create('tf_id', '', 'small', size_threshold=6,
                                 context=self.portal)
        self.assertTrue(isinstance(tf, File))

        # From str, big enough
        tf = TramlineFile.create('tf_id', '', 'big enough', size_threshold=6,
                                 context=self.portal)
        self.assertTrue(isinstance(tf, TramlineFile))
        fh = open(tf.getFullFilename(), 'r')
        self.assertEquals(fh.read(), 'big enough')
        fh.close()

        # from a real FS file. Must work even if unlinked
        tmp = tempfile.TemporaryFile() # on *nix, this is unlinked
        tmp.write('big enough') # no seek(0)

        tf = TramlineFile.create('tf_id', '', tmp, size_threshold=6,
                                 context=self.portal)
        self.assertTrue(isinstance(tf, TramlineFile))
        fh = open(tf.getFullFilename(), 'r')
        self.assertEquals(fh.read(), 'big enough')
        fh.close()

    def testTitleModification(self):
        fobj = self.tramfile
        old_title = fobj.title

        ttool = self.portal.portal_tramline
        dm = self.fproxy.getContent().getDataModel(proxy=self.fproxy)
        dm['file'].title = 'newreport.pdf'
        dm._commit(check_perms=False)

        fobj = self.fproxy.getContent().file
        lnpath = ttool.getHumanReadablePath(str(fobj), fobj.title)
        self.assertTrue(os.path.islink(lnpath))
        realpath = os.path.realpath
        self.assertEquals(realpath(lnpath), realpath(fobj.getFullFilename()))

        # consistency check: tramline file instance has been replaced, i.e
        # deletion followed by addition
        from Products.CPSTramline.transactional import get_txn_manager
        get_txn_manager().doCommit()
        self.assertTrue(os.path.islink(lnpath))
        self.assertTrue(os.path.isfile(fobj.getFullFilename()))
        self.assertEquals(realpath(lnpath), realpath(fobj.getFullFilename()))
        # finally, old symlink has been deleted
        old_lnpath = ttool.getHumanReadablePath(str(fobj), old_title)
        self.assertFalse(os.path.islink(old_lnpath))

    def test_size(self):
        fobj = self.tramfile
        self.assertEquals(fobj.get_size(), 17L)
        fobj.actual_size = None
        self.assertEquals(fobj.get_size(), 17L)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TramlineFileTestCase),
        ))


