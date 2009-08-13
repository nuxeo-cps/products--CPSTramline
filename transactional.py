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
# $Id: transactional.py 973 2008-10-20 07:03:15Z joe $
"""Manager to manipulate tramline repo when transactions finish."""

import os
import logging

import transaction
import zope.interface

from Acquisition import aq_base

from Products.CPSCore.interfaces import IAfterCommitSubscriber
from Products.CPSCore.commithooks import AfterCommitSubscriber
from Products.CPSCore.commithooks import get_after_commit_subscribers_manager

_TXN_MGR_ATTRIBUTE = '_cps_tramline_manager'

# We don't want any other hooks executed before this one right now.  It
# will have an order of -100
_TXN_MGR_ORDER = -100

logger = logging.getLogger("CPSTramline.TransactionManager")

class TransactionManager(AfterCommitSubscriber):
    """Holds data about reindexings to be done."""

    zope.interface.implements(IAfterCommitSubscriber)

    def __init__(self, mgr):
        """Initialize and register this manager with the transaction."""
        AfterCommitSubscriber.__init__(self, mgr, order=_TXN_MGR_ORDER)
        self._to_del = set()
        self._created = set()

    def toDelete(self, path):
        """Register a path for after commit deletion."""

        if not self.enabled:
            logger.debug("is DISABLED. path '%s' won't be processed", path)
            return

        logger.debug("registering for deletion: %s", path)
        self._to_del.add(path)

    def unDelete(self, *paths):
        """Unregister a path."""
        if not self.enabled:
            logger.debug("is DISABLED. path '%s' won't be processed", path)
            return

        for path in paths:
            self._to_del.discard(path)
            logger.debug("UNregistering deletion of: %s", path)

    def created(self, *paths):
        """Register a path as created within the transaction."""
        logger.debug("registering created paths: %s", paths)
        self._created.update(paths)

    def __call__(self, status=False):
        """Called when transaction has committed.

        Does the actual removal of files.
        """
        if status:
            self.doCommit()
        else:
            self.doAbort()

    def doCommit(self):
        for path in self._to_del:
            logger.debug("commit: removing file path=%s", path)
            try:
                if (os.path.isfile(path)):
                    os.remove(path)
                else:
                    logger.warn("file '%s' doesn't exist", path)
            except os.error, e:
                logger.error("OSError while trying to remove '%s': %s",
                          path, str(e))

    def doAbort(self):
        # TODO GR: code doesn't seem to be executed anymore
	# after commit hook system has changed ?
        for path in self._created:
            logger.debug("abort: removing file path=%s", path)
            try:
                if (os.path.isfile(path)):
                    os.remove(path)
                else:
                    logger.warn("file '%s' doesn't exist", path)
            except os.error, e:
                logger.error("OSError while trying to remove '%s': %s",
                          path, str(e))

def get_txn_manager():
    """Get the transation manager.

    Creates it if needed.
    """
    txn = transaction.get()
    mgr = getattr(txn, _TXN_MGR_ATTRIBUTE, None)
    if mgr is None:
        mgr = TransactionManager(get_after_commit_subscribers_manager())
        setattr(txn, _TXN_MGR_ATTRIBUTE, mgr)
    return mgr
