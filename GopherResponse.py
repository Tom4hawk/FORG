# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Released under the terms of the GNU General Public License
#
# This object holds the data corresponding to how a gopher server responded
# to a given request.  It holds one of two things in general, either a pile
# of data corresponding to text, a gif file, whatever, or it holds a list of
# GopherResource objects.  (This is when it's a directory entry that's being
# stored.
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
##############################################################################
import re
from urllib.parse import *
from gopher import *
import Connection
import GopherConnection
import GopherObject
import GopherResource
import ResourceInformation
import Options


class GopherException(Exception):
    pass


class GopherConnectionException(Exception):
    pass


class GopherResponseException(Exception):
    def __init__(self, message):
        super(GopherResponseException, self).__init__(message)


class GopherResponse(GopherObject.GopherObject):
    verbose = None

    def __init__(self, type=None, host=None, port=None, loc=None, name=None):
        GopherObject.GopherObject.__init__(self, type, host, port, loc, name)
        self.__class = "GopherResponse"
        self.data = None
        self.responses = []

    def toProtocolString(self):
        if self.getData() is None:
            return "".join(list(map(lambda x: x.toProtocolString(), self.getResponses())))
        else:
            return self.getData()

    def writeToFile(self, filename):
        """Writes the contents of this response to a disk file at filename
        this may raise IOError which the caller should deal with"""
        fp = open(filename, "w")
        
        if self.getData() == None:
            for resp in self.getResponses():
                fp.write(resp.toProtocolString())
        else:
            fp.write(self.getData())

        fp.flush()
        fp.close()
        return filename

    def getResponses(self):
        """Return a list of responses.  This is only really good when the
        response was a directory and set of entries."""
        if self.getData() != None:
            raise GopherResponseException("Get data instead.")
        return self.responses

    def getData(self):
        """Return the data associated with the response.  This is usually all
        of the data off of the socket except the trailing closer."""
        return self.data

    def getDataLength(self):
        return len(self.data)

    def getDataChunk(self, startIndex, endIndex=-1):
        """This method provides a way to get chunks of data at a time,
        rather than snarfing the entire ball."""
        
        if endIndex == -1:
            endIndex = len(self.data)
        return self.data[startIndex, endIndex]

    def getError(self):
        """If there was an error message, return it."""
        try:
            return self.error
        except:
            return None

    def setError(self, errorstr):
        """Modify the error message within this response."""
        self.error = errorstr
        return self.getError()

    def setData(self, data):
        """Modify the data within the response.  You probably don't want to
        do this."""
        self.data = data
        return None

    def looksLikeDir(self, data):
        """Takes a chunk of data and returns true if it looks like directory
        data, and false otherwise.  This is tricky, and is of course not 100%.
        Basically, we look at each line, see if the first bit in the line is a
        legal type, check to see that the line has at least 3 tabs in it.  If
        all of the first 20 lines of the data follow that rule, then it's good
        enough to be used as directory data.  If not, it gets chucked.  Notice
        that if this really is a directory but it's using file types we've
        never heard of (see gopher.py) then it will still get thrown out.
        Bummer.  This should only be called anyway if the type indictator is
        incorrect, so cope.  :)"""
        
        def linefn(l):
            return l.replace("\r", "")

        # Some very strange non-standards compliant servers send \r on some
        # lines and not on others.  So split by newline and remove all
        # carriage returns as they occur.
        lines = list(map(linefn, data.split("\n", 10)))

        for line in lines:
            d = line.strip()
            if not d or d == '' or d == '.':
                continue
            
            if line.count("\t") < 2:
                return None               # Not enough tabs.  Bummer.

            isResponse = None
            byte = line[0]
            try:
                resp = responses[byte]
                isRespose = 1
            except:
                pass

            if isResponse:
                continue
            
            try:
                resp = errors[byte]
            except:
                return None

        if len(lines) > 0:
            return 1     # Matched all tests for max 20 lines.  Looks OK.
        else:
            return 0     # Empty data isn't a directory.
    
    def parseResponse(self, data):
        """Takes a lump of data, and tries to parse it as if it was a directory
        response.  It will set the responses array to the proper thing if the
        result was good, so that you can use self.getRepsonses() to access
        them.  Otherwise it raises GopherResponseException"""
        
        self.responses = []

        if self.type == RESPONSE_DIR:
            pass          # Keep going
        elif self.looksLikeDir(data):
            self.type = RESPONSE_DIR
        else:
            raise GopherException("This isn't a directory.")

        def stripCR(dat):
            return dat.replace("\r", "")

        # This is done because \r may or may not be present, so we can't
        # split by \r\n because it fails for some misbehaved gopher servers.
        self.lines = list(map(stripCR, data.split("\n")))

        for line in self.lines:
            if len(line) <= 1:
                continue

            # Type of the resource.  See gopher.py for the possibilities.
            stype = "%s" % line[0]
            line = line[1:]

            # Gopher protocol uses tab delimited fields...
            linedata = line.split("\t")
            name    = "Unknown"              # Silly defaults
            locator = "Unknown"
            host    = "Unknown"
            port    = 70

            try:
                name = linedata[0]           # Assign the right things in the
            except IndexError: pass          # right places (maybe)
            try:                             # Catch those errors coming from
                locator = linedata[1]        # the line not being split into 
            except IndexError: pass          # enough tokens.  Realistically,
            try:                             # if those errors happen,
                host = linedata[2]           # something is really screwed up
            except IndexError: pass          # and there's not much we can do
            try:                             # anyway.  
                port = linedata[3]
            except IndexError: pass

            try:
                remainder = linedata[4:]     # Extra Gopher+ fields.
            except:
                remainder = []

            # UMN gopherd errors do this sometimes.  It's quite annoying.
            # they list the response type as 'directory' and then put the host
            # as 'error.host' to flag errors
            if host == 'error.host' and stype != RESPONSE_BLURB:
                stype = RESPONSE_ERR

            newresource = GopherResource.GopherResource(stype, host,
                                                        port, locator, name,
                                                        remainder)
            
            # Are the options set to allow us to get info?
            # THIS SHOULD BE USED WITH CAUTION since it can slow things down
            # more than you might think.
            if Options.program_options.getOption('grab_resource_info'):
                if len(remainder) >= 1 and remainder[0] == '+':
                    try:
                        conn = GopherConnection.GopherConnection()
                        info = conn.getInfo(newresource)
                        newresource.setInfo(info)
                    except GopherConnectionException as estr:
                        print("***(GCE) can't get info: %s" % estr)
                    except Exception as estr:
                        print("***(unknown) Couldn't %s %s" % (Exception,estr))

            self.responses.append(newresource)
        return None
# End GopherResponse
