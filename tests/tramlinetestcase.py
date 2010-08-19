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
# $Id$

import unittest
from Testing.ZopeTestCase import ZopeTestCase
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from layer import CPSTramlineLayer

import os

from Products.CPSTramline.tool import TramlineTool

TEST_DATA_PATH = os.path.join(os.path.split(__file__)[0], 'data')

class TramlineMixin:
    """Test case providing fixture with a tramline repository."""

    def createToolAndHierarchy(self):
        self.tool = TramlineTool()
        self.createHierarchy(self.tool)

    def createHierarchy(self, tool):
        self.tramline_path = base_path = os.tmpnam()  # security not an issue
        tool.tramlinepath = base_path # some tests my change it

        tool.relative = False

        os.mkdir(base_path)
        for name in ('repository', 'upload',):
            os.mkdir(os.path.join(base_path, name))

    def removeHierarchy(self):
        # not portable, but CPSTramline if for *nix anyway
        os.system('rm -r  %s' % self.tramline_path)

class TramlineTestCase(TramlineMixin, unittest.TestCase):

    def setUp(self):
        self.createToolAndHierarchy()

    def tearDown(self):
        self.removeHierarchy()

class ZopeTramlineTestCase(TramlineMixin, ZopeTestCase):

    def afterSetUp(self):
        self.createToolAndHierarchy()
        self.folder._setObject('portal_tramline', self.tool)
        self.tool = self.folder.portal_tramline

    def beforeTearDown(self):
        self.removeHierarchy()

class CPSTramlineTestCase(TramlineMixin, CPSTestCase):

    layer = CPSTramlineLayer

    def afterSetUp(self):
        self.createHierarchy(self.portal.portal_tramline)

    def beforeTearDown(self):
        self.removeHierarchy()
