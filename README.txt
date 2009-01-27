==================
CPSTramline README
==================

:Author: Georges Racinet

:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4

This product integrates CPS with Infrae Tramline.

Requirement: CPS 3.4.x, with CPSSchemas >= 1.7.1

It defines CPSTramlineFileField and CPSTramlineFileWidget as well as
mixin classes to easily enhance
fields and widgets derived from CPSField and CPSAttachedFileWidget
with tramline capability.

CPS can access the content from the tramline repository for further
processing, as provided, e.g, by PortalTransforms.

There are two configuration profiles:
   - The minimal profile creates the tramline tool
   - The default profile changes the 'file' schema and layout to enable
   tramline.

IMPORTANT: LIMITATIONS
======================

   - This product will work properly under Unixes systems only.
   - Doesn't handle Zope OFS.Image instances yet, hence CPSImageWidget
   and friends won't work.
   - Dependent fields of CPSFileField (html and text transforms) haven't been
     ported yet. Therefore indexing won't work

INSTALLATION
============

   - use the patched tramline and follow its installation
     instructions (INSTALL.txt),
     including mod_python's apache.py patch and virtual host
     configuration.

     This patched tramline is available as a svn checkout:
     svn co https://svn.nuxeo.org/pub/vendor/tramline/branches/gracinet-fix-range/

     For the record the code was previously present at the following URL:
     http://svn.viral-prod.com/tramline/trunk/

   - make sure that Zope has a write access to Tramline's repository.

     The recommended way to do that is to
       + put Zope's effective user in the apache group
         (e.g, www-data with Debian GNU/Linux)
       + add the following in the virtual host configuration:
	 PythonOption allow_group_write True

   - Restrict Tramline to work only for "tramlined" widgets

     If you don't do this, then all files from HTTP POST requests will
     be tramlined. Therefore, you'll need to upgrade all your widgets
     to work with tramline. See above for OFS.Image limitation.

     In the virtual host, put this
         PythonOption explicit_enable="true"
     
   - Pass the CPS Tramline Minimal profile (at least).

   - Enable tramline for your custom (non CPSDefault) content. 

     Read this if you want to enable tramline for custom document types whose
     list of layouts doesn't start with 'common'.

     *Manual enabling*:

     With the 'explicit_enable' PythonOption above, one has to insert an hidden
     input in each <form> with tramlined inputs. Furthermore, all tramlined 
     inputs of the form have to occur after this hidden input to be activated.
  
     More precisely, the form of the input is:
     <input type="hidden" name="tramline_enable" 
            value=VALUE>
     where VALUE is the space separated list of 
     'name' attributes of all <input> elements that must be tramlined. 

     *The Tramline Enabler Widget*:

     A better way in the CPS context is to ensure that all your tramlined 
     widgets lie in a layout *after* an instance of "Tramline Enabler
     Widget" and they will automatically declare themselves to the listening 
     Tramline filter. This special widget takes care of declaring inputs for 
     all tramline aware widgets is transparent for the others. 
     Multiple instances in a single portal_type of this special widget 
     don't harm. The CPS Tramline minimal profile inserts one in the 
     'common' layout. 

     Therefore you only need to put an instance of this widget  in your layouts
     if your documents don't have the 'common' layout or you have tramline 
     content before this layout (in that latter case take care of choosing 
     a different widget id)

   - Import the CPS Tramline Default OR the CPS Tramline Big File profiles 
     (optional)

     The CPS Tramline Default profile tramlines Attached File Widgets 
     for 'file' and 'flexible_content' layouts.

     The CPS Tramline Big File profile creates a new document type (Big File)
     that has to size limitations and adds also a big file widget in standard
     flexible layouts. All these file widgets are tramlined. The standard file
     layout is untouched, safe for the size limitation that goes to 1MB.

     These two profiles are (lightly) incompatible in the hard and anyway serve
     obviously different purposes

   - Go to the Tramline Tool (portal_tramline) and, if needed, correct
     the tramline path.

   - Tramline your custom layouts (if any need to)

     You just have to change  "Attached File Widget" instances to 
     "Tramline Attached File Widget" 
     (resp. "File Widget" to "Tramline File Widget). 

     This is what the CPS Tramline Default profile does for the 'file' 
     and 'flexible_content' layouts.

EXISTING CONTENT
================

   Existing content will be served as before. Any modification going
   through a Tramline aware widget will store the new content within
   Tramline.

TRAMLINING CUSTOM WIDGETS
=========================

     Any widget whose input field has been tramlined will have to be
     tramline-aware, which can be done by applying the TramlineMixin 
     class - put it first in the inheritance.

     This product provides the builtin "Tramline Attached File Widget", 
     for immediate use and as an example. 

     Check how it's been defined in widgets.py to learn how to apply 
     the mixin class to your own widget classes, assuming that 
     they do inherit from CPSFileWidget. 


.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:
