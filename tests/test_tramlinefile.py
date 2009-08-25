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
from Products.CPSTramline.tramlinefile import TramlineFile

class TramlineFileTestCase(CPSTramlineTestCase):

    def clearTestRepo(self):
        # Make platform-indepent ?
        os.system('rm -r %s' % TESTREPO)

    def afterSetUp(self):
        CPSTramlineTestCase.afterSetUp(self)

        ttool = self.ttool = self.portal.portal_tramline

        self.login('manager')
        wftool = self.portal.portal_workflow
        wftool.invokeFactoryFor(self.portal.workspaces, 'File', 'the_file')
        fproxy = self.portal.workspaces.the_file
        dm = fproxy.getContent().getDataModel(proxy=fproxy)
        dm['file'] = TramlineFile('file', 'report.pdf', 'some_tramid',
                                  actual_size=17L)
        dm._commit()
        self.fproxy = self.portal.workspaces.the_file
        self.tramfile = self.fproxy.getContent().file

        # simulate creation of file by tramline within Apache server
        fd = open(self.tramfile.getFullFilename(), 'w')
        fd.write('a' * 17)
        fd.close()

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


