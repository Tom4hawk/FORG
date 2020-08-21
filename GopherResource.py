# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# This class defines the information needed for a gopher resource.  That
# usually contains all the needed information about one instance of a file,
# directory, or other "thingy" on a gopher server.  This class extends
# GopherObject which gives it most of its accessors/mutators.
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
from urllib.parse import *
from gopher import *
import GopherConnection
import GopherObject
# import Options

class GopherResource(GopherObject.GopherObject):
    verbose   = None
    debugging = None  # Set to true for messages at the prompt, etc.
    def __init__(self,
                 type       = RESPONSE_DIR,
                 host       = "gopher.floodgap.com",
                 port       = 70,
                 locator    = "/",
                 stringName = "",
                 auxFields  = []):
        GopherObject.GopherObject.__init__(self, type, host, port, locator, stringName)
        self.__class = "GopherResource"
        if self.debugging:
            print("NEW GOPHER RESOURCE: " + self.toString())
        self.info = None
        self.setAuxFields(auxFields)
            
        return None
    
    def setInfo(self, newinfo):
        self.info = newinfo
        return self.info
    
    def getInfo(self, shouldFetch=None):
        """Returns the ResourceInformation block associated with this
        Resource.  If shouldFetch is true, the resource block will fetch
        information about itself if none is present."""
        if not self.info and shouldFetch:
            try:
                self.setInfo(conn.getInfo(self))
            except Exception as errstr:
                print("**** GopherResource couldn't get info about itself:")
                print(errstr)
                # This is bad.
                self.setInfo(None)

        return self.info
    
    def setAuxFields(self, fields):
        self.auxFields = fields

        if len(self.auxFields) > 0 and self.auxFields[0] == '?':
            # We need to fetch information about this one, since it's
            # going to contain ASK blocks.
            conn = GopherConnection.GopherConnection()
            
            try:
                self.setInfo(conn.getInfo(self))
            except Exception as errstr:
                print("**** GopherResource couldn't get info about itself:")
                print(errstr)
                # This is bad.
                self.setInfo(None)
        
        return self.auxFields
    
    def getAuxFields(self):
        return self.auxFields

    def isAskType(self):
        if not self.isGopherPlusResource():
            return None

        if len(self.auxFields) > 0 and self.auxFields[0].strip() == '?':
            return 1
        else:
            return None
        return None
    
    def isGopherPlusResource(self):
        if len(self.auxFields) > 0:
            return 1
        else:
            return None
    
    def toProtocolString(self):
        """Overrides the GopherObject method of the same name to provide
        support for printing out the auxFields in this object."""
        return "%s%s\t%s\t%s\t%s\t%s\r\n" % (self.getTypeCode(),
                                             self.getName(),
                                             self.getLocator(),
                                             self.getHost(), self.getPort(),
                                             "\t".join(self.getAuxFields()))
    
    def toXML(self):
        """Returns a small XML tree corresponding to this object.  The root
        element is the name of the object.  Override me in subclasses."""
        tags = [["type",    self.getType()],
                ["locator", self.getLocator()],
                ["host",    self.getHost()],
                ["port",    self.getPort()],
                ["name",    self.getName()]]

        str = "<GopherResource>"
        for tag in tags:
            str = str + "<%s>%s</%s>" % (tag[0], tag[1], tag[0])
        str = str + "</GopherResource>"

        return str

    def toURL(self):
        """Return the URL form of this GopherResource"""
        return "gopher://%s:%s/%s%s" % (self.getHost(), self.getPort(),
                                        self.getTypeCode(),
                                        self.getLocator())
    
    def setURL(self, URL):
        """Take a URL string, and convert it into a GopherResource object.
        This destructively modifies this object and returns a copy of itself

        FROM RFC 1738:
        Gopher URLs look like this:

        gopher://host:port/TypeCodeLocator

        where TypeCode is a one-character code corresponding to some entry
        in gopher.py  (hopefully) and Locator is the locator string for the
        resource.
        """
        thingys  = urlparse(URL)
        type     = thingys[0]
        hostport = thingys[1]
        resource = thingys[2]
        sublist  = hostport.split(":", 2)
        host     = sublist[0]
        
        try:
            port     = sublist[1]
            port     = int(port)
        except IndexError:
            port     = 70
        except ValueError:
            port     = 70

        self.setHost(host)
        self.setPort(port)

        # Strip the leading slash from the locator.  
        if resource != '' and resource[0] == '/':
            resource = resource[1:]

        if len(resource) >= 2:
            newtypecode = resource[0]
            locator = resource[1:]
        else:
            newtypecode = RESPONSE_DIR
            locator = "/"
            
        self.setLocator(locator)
        self.setName(self.getLocator())
        self.setTypeCode(newtypecode)
        return self # Return a copy of me

# End GopherResource

def URLtoResource(URL):
    """Non-class method mimicing GopherResource.setURL"""
    res = GopherResource()
    return res.setURL(URL)

