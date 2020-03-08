# Bookmark.py
# $Id: Bookmark.py,v 1.14 2001/07/11 22:43:09 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# This is a subclass of GopherResource and is used in the Bookmark
# management system of the FORG.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
############################################################################
import xml.etree.ElementTree as ETs
import GopherResource


class Bookmark(GopherResource.GopherResource):
    def __init__(self, res=None):
        GopherResource.GopherResource.__init__(self)

        if res != None:
            # Copy data from the resource to this bookmark.
            self.setName(res.getName())
            self.setHost(res.getHost())
            self.setPort(res.getPort())
            self.setLocator(res.getLocator())
            self.setType(res.getTypeCode())

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def toXML(self):
        """Returns an XML representation of the object."""
        bookmark = ETs.Element("bookmark", href=self.getURL())
        title = ETs.Element("title")
        title.text = self.getName()
        bookmark.append(title)

        return bookmark

    def getURL(self):
        return self.toURL()

    def toData(self):
        return "%s !! gopher://%s:%s/%s" % (self.getName(), self.getHost(),
                                            self.getPort(), self.getLocator())

    def toString(self):
        if self.getName() != '':
            return "%s: %s" % (self.getHost(), self.getName())
        elif self.getLocator() == '/' or self.getLocator() == '':
            return "%s Root" % self.getHost()
        else:
            return "%s:%s %s" % (self.getHost(), self.getPort(), self.getLocator())
