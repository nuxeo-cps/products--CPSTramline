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
        dm['file'] = TramlineFile('file', 'report.pdf', 'some_tramid')
        dm._commit()
        self.fproxy = self.portal.workspaces.the_file

    def testCreation(self):
        ttool = self.portal.portal_tramline
        fobj = self.fproxy.getContent().file
        lnpath = ttool.getHumanReadablePath(str(fobj), fobj.title)
        self.assertTrue(os.path.islink(lnpath))
        realpath = os.path.realpath
        self.assertEquals(realpath(lnpath), realpath(fobj.getFullFilename()))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TramlineFileTestCase),
        ))


