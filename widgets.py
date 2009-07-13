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
# $Id: widgets.py 973 2008-10-20 07:03:15Z joe $

import os
import logging

from Globals import InitializeClass
from OFS.Image import File

from Products.CMFCore.utils import getToolByName

from Products.CPSUtil.html import renderHtmlTag
from Products.CPSSchemas.Widget import widgetRegistry

from Products.CPSSchemas import BasicWidgets

from Products.CPSSchemas.Widget import CPSWidget
from Products.CPSSchemas.BasicWidgets import CPSFileWidget
from Products.CPSSchemas.ExtendedWidgets import CPSAttachedFileWidget

from tramlinefile import TramlineFile

from Products.CPSUtil.file import makeFileUploadFromOFSFile

TRAMLINE_DS_KEY = '_tramline_inputs'

# Patch to recognize file uploads built from preexisting OFS.File instances
def makeTramlineFileUpload(ofsfile):
    """Tramline aware variant.

    Code can check if a file comes from a stored ofsfile that is not tramlined
    by a simple getattr(fileupload, 'not_tramline', False)
    """

    fu = makeFileUploadFromOFSFile(ofsfile)
    if fu is not None and not ofsfile.meta_type.startswith('Tramline'):
        fu.not_tramline = True
    return fu

BasicWidgets.makeFileUploadFromOFSFile = makeTramlineFileUpload

class TramlineWidgetMixin(object):
    """Mixin class to tramline a CPSFileWidget subclass.

    Put it first in multi-inheritance declaration.
    """

    log = logging.getLogger('Products.CPSTramline.TramlineWidgetMixin')

    def makeFile(self, filename, fileupload, datastructure):
        init = (self.fields[0], filename, fileupload)
        REQUEST = getattr(self, 'REQUEST', None)

        ### XXX could have tramline add something to file's Content-Dispo
        ### and check that
        if REQUEST is None:
            # No access to request from there, default to a good old file
            return File(*init)
        else:
            REQUEST.RESPONSE.setHeader('tramline_ok','')
            return TramlineFile(*init)

    def getFileSize(self, fileupload):
        if getattr(fileupload, 'not_tramline', False):
            return CPSFileWidget.getFileSize(self, fileupload)
        trtool = getToolByName(self, 'portal_tramline')
        tramid = fileupload.read()
        self.log.debug("Tramline id: %s", tramid)
        # correct with actual size
        try:
            return os.path.getsize(trtool.getFilePath(tramid, allow_tmp=True))
        except os.error:
            self.log.error(
                "OS error while trying to retrieve size of tramline file '%s'",
                tramid)

    def prepare(self, ds, **kw):
        """Add this widget's input id to ds and call back normal prepare()"""
        # no need to use a set
        ds.setdefault(TRAMLINE_DS_KEY, []).append(self.getHtmlWidgetId())
        # since we inherit directly from object, and as a mixin, impose to be
        # first in multi-inheritance applications, there's no ambiguity with 
        # super(). See http://fuhm.net/super-harmful for explanation
        super(TramlineWidgetMixin, self).prepare(ds, **kw)

class TramlineEnablerWidget(CPSWidget):
    """Used to render a hidden input for tramline enabling."""
    
    meta_type = "Tramline Enabler Widget"
    fields = ()

    def validate(self, datastructure, **kw):
	return True

    def prepare(self, datastructure, **kw):
        pass

    def render(self, mode, ds, **kw):
        """Render an hidden input with all the tramlined inputs.
        
        Do it only once in case there are two instances of this widget
        (hard to avoid)
        """
        if mode != 'edit':
            return ''
        inputs = ds.pop(TRAMLINE_DS_KEY, None)
        if inputs is None:
            return ''

        # XXX currently, tramline doesn't support properly the enabling
        # of several inputs. This would work if there was an additional
        # split() in tramline/core.py for instance
        return renderHtmlTag('input',
                             type='hidden',
                             name='tramline_enable',
                             value=' '.join(inputs))
        
InitializeClass(TramlineEnablerWidget)
widgetRegistry.register(TramlineEnablerWidget)

class CPSTramlineAttachedFileWidget(TramlineWidgetMixin, CPSAttachedFileWidget):
    """Tramline enhanced."""
    meta_type = "Tramline Attached File Widget"
    manage_options = CPSAttachedFileWidget.manage_options
InitializeClass(CPSTramlineAttachedFileWidget)
widgetRegistry.register(CPSTramlineAttachedFileWidget)

class CPSTramlineFileWidget(TramlineWidgetMixin, CPSFileWidget):
    """Tramline enhanced."""
    meta_type = "Tramline File Widget"

InitializeClass(CPSTramlineFileWidget)
widgetRegistry.register(CPSTramlineFileWidget)

