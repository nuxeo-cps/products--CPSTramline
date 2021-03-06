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

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION
from Products.CPSCore.upgrade import registerUpgradeCategory

from Products.CMFCore.DirectoryView import registerDirectory

from Products.CPSCore.interfaces import ICPSSite

import widgets
import externaleditor

registerDirectory('skins', globals())

# registration for ExternalEditor
try:
    from Products.ExternalEditor.ExternalEditor import registerCallback \
        as ee_register_cb
except ImportError:
    raise
else:
    ee_register_cb(externaleditor.callback)


# registration for auto content creation (#2205, #2208)
from tramlinefile import TramlineFile, TramlineImage
from Products.CPSSchemas.BasicFields import CPSFileField, CPSImageField
from Products.CPSSchemas.FileUtils import FileObjectFactory

# GR this was done for #2205. This looks wrong but isn't.
# Namely, one could think that this leads to TramlineFile object creations
# for portals that are not tramline enabled (wrong), but actually, the create
# classmethod degrades gracefully to good old OFS.Image objects if the
# tramline tool is not there (right).
FileObjectFactory.methods[CPSFileField.meta_type] = (
    TramlineFile.create, dict(context=True, size_threshold=40960)) # 40 kB
FileObjectFactory.methods[CPSImageField.meta_type] = (
    TramlineImage.create, dict(context=True, size_threshold=40960)) # 40 kB

def is_category_applicable(portal):
    return portal.hasObject('portal_tramline')

registerUpgradeCategory('cpstramline',
                        title='CPS Tramline',
                        floor_version='0.10.0',
                        ref_product='CPSTramline',
                        description='Tramline integration',
                        is_applicable=is_category_applicable,
                        portal_attribute='upgraded_cpstramline_version')

from Products.CPSUtil.genericsetup import tool_steps
export_step, import_step = tool_steps('portal_tramline', logger_id='tramline')


def initialize(registrar):

    # Profile registry
    profile_registry.registerProfile(
        'minimal',
        'CPS Tramline Minimal',
        "CPS Tramline minimal enabling.",
        'profiles/minimal',
        'CPSTramline',
        EXTENSION,
        for_=ICPSSite)

    profile_registry.registerProfile(
        'cpsdefault-all',
        'CPS Tramline Full for CPSDefault',
        "Full CPS Tramline integration for the whole of CPSDefault",
        'profiles/cpsdefault-all',
        'CPSTramline',
        EXTENSION,
        for_=ICPSSite)

    profile_registry.registerProfile(
        'bigfile',
        'CPS Tramline Big File',
        "CPS Tramline integration that adds a new 'Big File' document type.",
        'profiles/bigfile',
        'CPSTramline',
        EXTENSION,
        for_=ICPSSite)


