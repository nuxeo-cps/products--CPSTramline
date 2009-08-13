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
from Products.CPSTramline.tool import HR_AREA
from Products.CPSTramline import upgrades

class UpgradesTestCase(CPSTramlineTestCase):

    def afterSetUp(self):
        CPSTramlineTestCase.afterSetUp(self)

        ttool = self.ttool = self.portal.portal_tramline
        self.setup_tool = self.portal.portal_setup

        self.login('manager')
        wftool = self.portal.portal_workflow
        wftool.invokeFactoryFor(self.portal.workspaces, 'File', 'the_file')
        fproxy = self.portal.workspaces.the_file
        dm = fproxy.getContent().getDataModel(proxy=fproxy)
        dm['file'] = TramlineFile('file', 'report.pdf', '0001')
        dm._commit()

        # an archived file: present in CPS' repository, but no proxy
        wftool.invokeFactoryFor(self.portal.workspaces, 'File', 'archived_file')
        fproxy = self.portal.workspaces.archived_file
        dm = fproxy.getContent().getDataModel(proxy=fproxy)
        dm['file'] = TramlineFile('file', 'archived.pdf', '0002')
        dm._commit()
        self.portal.workspaces.manage_delObjects(['archived_file'])


    def test_add_symlink_for_all(self):
        hr_path = os.path.join(self.tramline_path, HR_AREA)
        os.system('rm -r %s' % hr_path)
        upgrades.add_symlinks_for_all(self.portal)
        self.assertEquals(os.listdir(hr_path), ['archived-0002.pdf',
                                                'report-0001.pdf'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UpgradesTestCase),
        ))


