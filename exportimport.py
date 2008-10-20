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
# $Id: exportimport.py 973 2008-10-20 07:03:15Z joe $
"""Tramline Tool XML Adapter.
"""

# Zope3 component architecture
from zope.component import adapts
from zope.interface import implements

# Standard GenericSetup base classes and functions
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import ObjectManagerHelpers

from Products.CMFCore.utils import getToolByName

# GenericSetup multi adapts a class that implement IVogonTool and a particular
# ISetupEnvironment to and IBody (piece of XML configuration).
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron

from interfaces import ITramlineTool

TOOL = 'portal_tramline'
NAME = 'tramline'

def exportTramlineTool(context):
    """Export our Tramline tool configuration
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL, None)
    if tool is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    exportObjects(tool, '', context)

def importTramlineTool(context):
    """Import viralprod tool configuration
    """
    site = context.getSite()
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)


# This the XMLAdapter itself. It encodes the im- / export logic that is specific
# to our tool. `im- / exportObjects` functions will find it thanks to the zope
# components machinery and the associations made in the configure.zcml file.

class TramlineToolXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for the Tramline tool.
    """

    adapts(ITramlineTool, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("Tramline tool exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._logger.info("Tramline tool imported.")
