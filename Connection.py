# Connection.py
# $Id: Connection.py,v 1.18 2001/09/02 17:02:23 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# Base class for socket connections.
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
import socket
import Options
from string import *
import utils
import errno


class ConnectionException(Exception):
    def __init__(self, message):
        super(ConnectionException, self).__init__(message)


class Connection:
    def __init__(self, *args):
        self._d = None
        self.bytes_transferred = {'sent'     : 0,
                                  'received' : 0 }

    def received(self, bytes):
        """Keep track of the number of bytes received on this socket object"""
        oldval = self.bytes_transferred['received']
        self.bytes_transferred['received'] = oldval + bytes
        return self.bytes_transferred['received']
    
    def sent(self, bytes):
        """Keep track of the number of bytes sent on this socket object"""
        self.bytes_transferred['sent'] = self.bytes_transferred['sent'] + bytes
        return self.bytes_transferred['sent']
    
    def getBytesSent(self):
        return self.bytes_transferred['sent']
    
    def getBytesRead(self):
        return self.bytes_transferred['received']
    
    def readloop(self, sock, bytesToRead, msgBar=None):
        """Reads bytesToRead data off of sock or until EOF if
        bytesToRead < 0.  Optionally uses msgBar to log information to the
        user."""
        timesRead = 0
        data      = ''
        CHUNKSIZE = 1024  # Default read block size.
                          # This may get overridden depending on how much data
                          # we have to read.  Optimally we want to read all of
                          # the data that's going to come in 100 steps.

        if bytesToRead < 0:
            numKBtoRead = ""   # Don't report total size since we don't know
        else:
            # Report the total size so the user has an idea of how long it's
            # going to take.
            val = float(bytesToRead) / float(1024)
            numKBtoRead = "of %0.2f kilobytes total size" % val

            if bytesToRead > (1024 * 100): # 100 Kb
                CHUNKSIZE = bytesToRead / 100

        chunk = 'foobar'
        
        while len(chunk) > 0:
            self.checkStopped(msgBar)        # Constantly make sure we should
            chunk = sock.recv(CHUNKSIZE)     
            self.received(CHUNKSIZE)
            self.checkStopped(msgBar)        # continue...
            
            timesRead = timesRead + 1
            # print "Read %s: %s" % (CHUNKSIZE, timesRead * CHUNKSIZE)
            data = data + chunk

            if bytesToRead > 0 and len(data) >= bytesToRead:
                # print "BTR=%s, len(data)=%s, breaking" % (bytesToRead,
                # len(data))

                # Disregard content length for broken gopher+ servers.
                # break
                pass
            
            if msgBar:
                # Report statistics on how far along we are...
                bytesRead = timesRead * CHUNKSIZE
                kbRead = (float(timesRead) * float(CHUNKSIZE)) / float(1024)

                if bytesToRead > 0:
                    pct = (float(bytesRead) / float(bytesToRead))*float(100)

                    # This happens sometimes when the server tells us to read
                    # fewer bytes than there are in the file. In this case,
                    # we need to only display 100% read even though it's
                    # actually more.  Becase reading 120% of a file doesn't
                    # make sense.
                    if pct >= float(100):
                        pct = float(100)
                    pctDone = ("%0.2f" % pct) + "%"
                else:
                    pctDone = ""

                msgBar.message('state',
                               "Read %d bytes (%0.2f Kb) %s %s" %
                               (bytesRead,
                                kbRead,
                                numKBtoRead,
                                pctDone))

        # Break standards-compliance because of all those terrible gopher
        # servers out there.  Return all of the data that we read, not just
        # the first bytesToRead characters of it.  This will produce the user
        # expected behavior, but it disregards content lenghts in gopher+
        if bytesToRead > 0:
            # return data[0:bytesToRead]
            return data
        else:
            return data

    def checkStopped(self, msgBar):
        """Issue a message to the user and jump out if greenlight
        isn't true."""
        if not Options.program_options.GREEN_LIGHT:
            raise ConnectionException("Connection stopped")

    def requestToData(self, resource, request,
                      msgBar=None, grokLine=None):
        """Sends request to the host/port stored in resource, and returns
        any data returned by the server.  This may throw
        ConnectionException.  msgBar is optional.
        May throw ConnectionException if green_light ever becomes false.
        This is provided so that the user can immediately stop the connection
        if it exists."""

        utils.msg(msgBar, "Creating socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not self.socket:
            raise GopherConnectionException, "Cannot create socket."

        self.checkStopped(msgBar)
        utils.msg(msgBar, "Looking up hostname...")
        try:
            # Try to get a cached copy of the IP address rather than
            # looking it up again which takes longer...
            ipaddr = Options.program_options.getIP(resource.getHost())
        except KeyError:
            # OK, it wasn't in the cache.  Figure out what it is,
            # and then put it in the cache.
            try:
                self.checkStopped(msgBar)
                ipaddr = socket.gethostbyname(resource.getHost())
            except socket.error as err:
                host = resource.getHost()
                estr = "Cannot lookup\n%s:\n%s" % (host, err)
                raise ConnectionException(estr)

        Options.program_options.setIP(resource.getHost(), ipaddr)
        
        # At this point, ipaddr holds the actual network address of the
        # host we're contacting.
        utils.msg(msgBar,
                  "Connecting to %s:%s..." % (ipaddr, resource.getPort()))
        try:
            retval = self.socket.connect((ipaddr, int(resource.getPort())))
            #if retval != 0:
            #    errortype = errno.errorcode[retval]
            #    raise socket.error, errortype
        except socket.error, err:
            newestr = "Cannot connect to\n%s:%s:\n%s" % (resource.getHost(),
                                                         resource.getPort(),
                                                         err)
            raise ConnectionException(newestr)
        
        data = ""

        self.checkStopped(msgBar)
        self.socket.send(request)    # Send full request - usually quite short
        self.checkStopped(msgBar)
        self.sent(len(request))      # We've sent this many bytes so far...

        if grokLine:   # Read the first line...this is for Gopher+ retrievals
            line = ""  # and usually tells us how many bytes to read later
            byte = ""
            
            while byte != "\n":
                self.checkStopped(msgBar)
                byte = self.socket.recv(1)
                if len(byte) <= 0:
                    print "****************BROKE out of byte loop"
                    break
                line = line + byte
    
            bytesread = len(line)
            line      = strip(line)

            try:
                if line[0] == '+':
                    bytecount = int(line[1:]) # Skip first char: "+-1" => "-1"
                    resource.setLen(bytecount)
                    
                    # Read all of the data into the 'data' variable.
                    data = self.readloop(self.socket, bytecount, msgBar)
                else:
                    data = self.readloop(self.socket, -1, msgBar)
            except:
                print "*** Couldn't read bytecount: skipping."
                data = self.readloop(self.socket, -1, msgBar)
        else:
            data = self.readloop(self.socket, -1, msgBar)

        utils.msg(msgBar, "Closing socket.")
        self.socket.close()

        # FIXME: 'data' may be huge.  Buffering?  Write to cache file here
        # and return a cache file name?
        return data
