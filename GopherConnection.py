# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Released under the terms of the GNU General Public License
#
# This object handles connections and sending requests to gopher servers.
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
#######################################################################
import socket
import re
import utils
import GopherResponse
import Connection
import GopherObject
import GopherResource
import ResourceInformation
import AskForm
from gopher import *

class GopherConnectionException(Exception):
    pass

class GopherConnection(Connection.Connection):
    SNARFSIZE                 = 1024
    verbose                   = None
    def __init__(self, server="gopher://gopher.floodgap.com", port=70):
        Connection.Connection.__init__(self)
        self.server = re.sub("gopher://", "", server, 1)
        self.port   = port
        self.forgetResponse()
        return None

    def forgetResponse(self):
        """Remove the response field of this object.  This is periodically
        necessary, since it can get quite large."""
        self.response = None
        return self.response
    def stripTail(self, data):
        ind = data.rfind("\r\n.\r\n")
        
        if ind != -1:
            if self.verbose:
                print("Stripping protocol footer at index %d" % int(ind))
            return data[0:ind]

        if self.verbose:
            print("No protocol footer found.")
        return data

    # Get extended information about a resource.
    def getInfo(self, resource, msgBar=None):
        try:
            req = "%s\t!\r\n" % resource.getLocator()
            data = self.requestToData(resource, req, msgBar)
        except Connection.ConnectionException as errstr:
            raise GopherConnectionException(errstr)
        
        if self.verbose:
            print("Got %d bytes from INFO conn:\n%s" % (len(data), data))

        # The server sends back a length of -2 when it doesn't know how long
        # the document is, and when the document may contain the \r\n.\r\n
        # pattern.  So if it might, do not strip it out.  Otherwise do.  This
        # will probably keep out a very subtle bug of having files downloaded
        # be truncated in really weird places.  (Where the \r\n.\r\n would have
        # been)
        if resource.getLen() != -2:
            if self.verbose:
                print("Stripping protocol footer.")
            data = self.stripTail(data)
            
        try:
            info = ResourceInformation.ResourceInformation(data)
        except Exception as estr:
            print("*********************************************************")
            print("***GopherConnection: ResourceInformation Error: %s" % estr)
            print("*********************************************************")
            raise GopherConnectionException(estr)
        
        return info
            
    def getResource(self, resource, msgBar=None):
        self.forgetResponse()
        self.host     = re.sub("gopher://", "", resource.getHost(), 1)
        self.port     = resource.getPort()
        self.lastType = resource.getType()

        try:
            if resource.getDataBlock():
                request = resource.getLocator() + "\t+\t1\r\n"
                request = request + resource.getDataBlock()
                
                self.response = self.requestToData(resource,
                                                   request,
                                                   msgBar, 1)
            elif resource.isGopherPlusResource() and resource.isAskType():
                info = resource.getInfo(shouldFetch=1)
                af = AskForm.AskForm(info.getBlock("ASK"))

                # Copy host/port/locator information into af
                af.dup(resource)
                return af
            elif resource.isGopherPlusResource():
                request = resource.getLocator() + "\t+\r\n"
                self.response = self.requestToData(resource,
                                                   request,
                                                   msgBar, 1)
            else:
                request = resource.getLocator() + "\r\n"
                self.response = self.requestToData(resource, request, msgBar, None)
        except Connection.ConnectionException as estr:
            error_resp = GopherResponse.GopherResponse()
            errstr = "Cannot fetch\n%s:\n%s" % (resource.toURL(), estr)

            error_resp.setError(errstr)
            return error_resp

        utils.msg(msgBar, "Examining response...")

        resp = GopherResponse.GopherResponse()
        resp.setType(resource.getTypeCode())

        if resource.getLen() != -2:
            self.response = self.stripTail(self.response)

        try:
            # The parser picks up directory entries and sets the internal
            # data of the object as needed.
            resp.parseResponse(self.response)

            # if we get this far, then it's a directory entry, so set the
            # data to nothing.
            resp.setData(None)
        except Exception as erstr:
            # print "Caught exception while parsing response: \"%s\"" % erstr
            if self.verbose:
                print("OK, it's data.")
            resp.setData(self.response)
                
        return resp
