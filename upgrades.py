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

import os
import logging

import transaction

from tramlinefile import TramlineFile

def add_symlinks_for_all(portal):
    ttool = portal.portal_tramline
    repotool = portal.portal_repository

    logger = logging.getLogger("Products.CPSTramline.upgrades#add_symlinks_for_all")
    logger.info("Scanning all documents in CPS repository f")
    total = len(repotool)
    done = 0
    for i, full_id in enumerate(repotool.objectIds()): 
        # objectIds seems to be a kind of iterator
        if i % 100 == 0:
            transaction.commit()
            logger.info("%d out of %d documents upgraded.", i+1, total)
        doc = repotool[full_id]
        logger.debug("Doc %s", doc)
        for obj in doc.objectValues(['Tramline File']):
            if ttool.makeSymlinkFor(obj, may_exist=True) is not None:
                done += 1

    logger.info("Finished. %d symbolic links have been created", done)

def recompute_size_for_all(portal):
    logger = logging.getLogger(
        "Products.CPSTramline.upgrades::recompute__size_for_all")
    logger.info("Scanning all documents in CPS repository f")

    repotool = portal.portal_repository
    total = len(repotool)
    done = 0
    for i, full_id in enumerate(repotool.objectIds()):
        # objectIds seems to be a kind of iterator
        if i % 100 == 0:
            transaction.commit()
            logger.info("%d out of %d documents upgraded.", i+1, total)
        doc = repotool[full_id]
        logger.debug("Doc %s", doc)
        fobjs = doc.objectValues(['Tramline File'])
        if not fobjs:
            continue
        for fobj in fobjs:
            fobj.actual_size = None # lazy computation
	# trigger all computations
	doc._size = doc._compute_size()
	logger.debug("Document %s, new size: %ld", doc, doc.get_size())
        # size information is not indexed yet
        done += 1

    logger.info("Finished. size of %d documents has been recomputed", done)
