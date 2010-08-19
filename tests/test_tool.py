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
# $Id: __init__.py 973 2008-10-20 07:03:15Z joe $

import unittest
from zope.testing import doctest

from tramlinetestcase import TramlineTestCase

class TramlineToolTestCase(TramlineTestCase):

    def testProperties(self):
        self.tool.manage_changeProperties(tramlinepath='/some/path',
                                          relative=False)
        self.assertEquals(self.tool.getTramlinePath(), '/some/path')

    def testExternal(self):
        # Here we DON'T WANT to check what the included tramline code exactly
        # produces: this is not CPSTramline's business. However we check that
        # it works and that the produced string is at least non empty
        self.tool.manage_changeProperties(tramlinepath='/some/path')
        self.assertTrue(self.tool.getFilePath('some_id'))


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.CPSTramline.tool',
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        unittest.makeSuite(TramlineToolTestCase),
        ))


