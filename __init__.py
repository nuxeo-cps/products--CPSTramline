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

from Products.CPSCore.interfaces import ICPSSite

import widgets

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
        'default',
        'CPS Tramline Default',
        "Full CPS Tramline default integration.",
        'profiles/default',
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


