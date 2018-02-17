# GopherObject.py
# $Id: GopherObject.py,v 1.17 2001/07/09 22:31:32 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
#
# Base class for GopherResource, GopherResponse
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
#############################################################################

import re
import os
import utils
from string import *
from gopher import *

class GopherObject:
    def __init__(self,
                 typecode = None,
                 host     = None,
                 port     = None,
                 locator  = None,
                 name     = None,
                 len      = -2):
        self.__class      = "GopherObject"
        self._shouldCache = "YES"
        self.setTypeCode(typecode)
        self.setHost(host)
        self.setPort(port)
        self.setLocator(locator)
        self.setName(name)
        self.setLen(len)
        self.setDataBlock("")
        return None
    def dup(self, res):
        """Returns a copy of this object."""
        self.setLen(res.getLen())
        self.setTypeCode(res.getTypeCode())
        self.setHost(res.getHost())
        self.setLocator(res.getLocator())
        self.setName(res.getName())
        self.setPort(res.getPort())
        return self
    # Accessors, mutators
    def shouldCache(self):
        return self._shouldCache
    def setShouldCache(self, boolval):
        self._shouldCache = boolval
        return self.getShouldCache()
    def getShouldCache(self):
        return self._shouldCache
    def getLen(self):
        return self.len
    def setLen(self, newlen):
        self.len = newlen
        return self.len
    def getTypeCode(self):
        return self.type[0]
    def setDataBlock(self, block):
        self.datablock = block
        return self.datablock
    def getDataBlock(self):
        return self.datablock
    def setType(self, newtype):
        return self.setTypeCode(newtype)
    def setTypeCode(self, newtype):
        self.type = newtype
        return self.type
    def getType(self):
        """Return a string representing the type code of the response.  See
        the gopher module for more information."""
        try:
            return responses[self.type]
        except KeyError:
            return "-Unknown-"
    def getHost(self):
        return self.host
    def setHost(self, newhost):
        self.host = newhost
        return self.host
    def getPort(self):
        return self.port
    def setPort(self, newport):
        self.port = newport
        return self.port
    def getLocator(self):
        return self.locator
    def setLocator(self, newlocator):
        self.locator = newlocator
        return self.locator
    def getName(self):
        if strip(self.name) == '/':
            self.setName("%s root" % self.getHost())
        elif self.name == '' or self.name is None:
            loc = strip(self.getLocator())
            if loc == '' or loc == '/':
                self.setName("%s root" % self.getHost())
            else:
                self.setName(" ")
                # self.setName("%s %s" % (self.getHost(), self.getLocator()))
        return self.name
    def setName(self, newname):
        self.name = newname
        return self.name
    # Methods
    def toURL(self):
        """Return the URL form of this GopherResource"""
        return "gopher://%s:%s/%s%s" % (self.getHost(),
                                        self.getPort(),
                                        self.getTypeCode(),
                                        re.sub("\t", "%9;", self.getLocator()))
    def toProtocolString(self):
        """Returns the protocol string, i.e. how it would have been served
        by the server, in a string."""
        return "%s%s\t%s\t%s\t%s\r\n" % (self.getTypeCode(),
                                         self.getName(),
                                         self.getLocator(),
                                         self.getHost(),
                                         self.getPort())
    def toXML(self):
        """Returns a small XML tree corresponding to this object.  The root
        element is the name of the object.  Override me in subclasses."""
        tags = [["type",    self.type],
                ["locator", self.locator],
                ["host",    self.host],
                ["port",    self.port],
                ["name",    self.name]]

        str = "<GopherObject>"
        for tag in tags:
            str = str + "<%s>%s</%s>" % (tag[0], tag[1], tag[0])
        str = str + "</GopherObject>"

        return str
    def __str__(self):
        return self.__class
        # return self.toString()
    def toString(self):
        """Returns a string form of this object.  Mostly only good for
        debugging."""
        return ("Type: %s\nLocator: %s\nHost: %s\nPort: %s\nName: %s\n" %
                (self.getTypeCode(), self.getLocator(),
                 self.getHost(), self.getPort(), self.getName()))

    def filenameToURL(self, filename):
        """Unencodes filenames returned by toFilename() into URLs"""        
        try:
            return utils.character_replace(filename, os.sep, "/")
        except:
            # os.sep is '/' - character_replace doesn't allow replacing a
            # character with itself.  we're running Eunuchs.
            return filename

    def toCacheFilename(self):
        filename = self.toFilename()
        lastchr = filename[len(filename)-1]
        if lastchr == os.sep or lastchr == '/':
            # Pray for no name clashes...  :)
            # We have to call it something inside the leaf directory, because
            # if you don't, you get into the problem of caching responses from
            # directories as files, and not having a directory to put the items
            # in the directory in.  And you can't call the file "" on any
            # filesystem.  :)
            filename = "%sgopherdir.idx" % filename
        elif self.getTypeCode() == RESPONSE_DIR:
            filename = "%s%sgopherdir.idx" % (filename, os.sep)

        port = self.getPort()
        str_to_find = ":%d" % int(port)

        # Cut out the port portion of the filename.  This is because some
        # OS's throw up with ':' in filenames.  Bummer, but this will make it
        # hard to translate a filename/path -> URL
        ind = find(filename, str_to_find)
        if ind != -1:
            filename = "%s%s" % (filename[0:ind],
                                 filename[ind+len(str_to_find):])

        if os.sep == '\\':       # No-name mac wannabe OS's... :)
            for char in ['/', ':', ';', '%', '*', '|']:
                # This isn't necessarily a good idea, but it's somewhat
                # necessary for windows boxen.
                filename = utils.character_replace(filename, char, ' ')
            
        return filename

    def toFilename(self):
        """Returns the name of a unique file containing the elements of this
        object.  This file is not guaranteed to not exist, but it probably
        doesn't. :)  Get rid of all of the slashes, since they are
        Frowned Upon (TM) by most filesystems."""

        replaceables = ['\t', '\n', '\\', '/']
        data = self.toURL()

        if find(lstrip(lower(data)), "gopher://") == 0:
            # Chomp the "gopher://" part
            data = data[len("gopher://"):]
        
        for r in replaceables:
            try:
                data = utils.character_replace(data, r, os.sep)
            except:
                pass

        return data
