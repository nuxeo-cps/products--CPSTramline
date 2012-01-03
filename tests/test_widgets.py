# (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from OFS.Image import File
from Products.CPSSchemas.widgets.file import makeFileUploadFromOFSFile
from Products.CPSTramline import widgets

class TramlineWidgetsTestCase(unittest.TestCase):

    def test_patch(self):
        f = File('fid', 'title', 'contents')
        fu = makeFileUploadFromOFSFile(f)
        self.assertTrue(fu.not_tramline)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TramlineWidgetsTestCase),
        ))


