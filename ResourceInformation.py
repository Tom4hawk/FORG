# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Released under the terms of the GNU General Public License
#
# When dealing with a Gopher+ server, information about a document can be
# fetched by sending the request:
# some_locator\t!\r\n
#
# This module handles the parsing and storing of that information.
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

from tkinter import *
import Pmw
import os
import re
import ContentFrame
from gopher         import *
import GopherResource
import GopherResponse

class ResourceInformation:
    verbose = None
    def __init__(self, data=None):
        self.blockdict = {}

        self.data = data
        
        if self.data != None:
            self.setData(self.data)

        return None
    def __str__(self):
        return self.toString()
    def toString(self):
        def fn(key, obj=self):
            return "%s:\n%s\n" % (key.upper(), obj.getBlock(key))
        
        return list(map(fn, self.getBlockNames())).join("") + "\n"
    
    def setData(self, data):
        self.data = data
        self.data = re.sub("\r\n", "\n", self.data)

        lastindex = -1
        blocks = []

        try:
            while 1:
                # This will throw ValueError if not found.
                newindex = index(self.data, "\n+", (lastindex + 1), len(self.data))
                blocks.append(self.data[lastindex+1:newindex])
                lastindex = newindex
        except ValueError:  # When no more "\n+" are found.
            # The remaining block is what's left...
            blocks.append(self.data[lastindex+1:len(self.data)])

        # What we're going to do is hash each data block in by its block
        # 'title'.  This way, when we're done hashing all of the data, we
        # can just go through and pick out what we want.  So this type of
        # data:
        # +ADMIN:
        #  Grendel The Evil <grendel@nowhere.com>
        #  Some more admin information
        # Gets hashed in like this essentially:
        # hash['admin'] = "Grendel The Evil <grendel@nowhere.com>\n..."
        self.blockdict = {}

        # We now have a list of blocks.
        for block in blocks:
            lines = block.split("\n")
            blocklabel = lines[0]

            front = blocklabel.find("+")   # This defines the start of a block
            back  = blocklabel.find(":")   # This may not be present

            if front != -1:
                if back == -1:
                    back = len(blocklabel)  # End of string if not present

                # Get the name, which is like this: "+ADMIN:" => 'ADMIN'
                blockname = blocklabel[front+1:back]
                key = blockname.lower() # Lowercase so it hashes nicely.  :)
                
                # strip the leading space.  This is because in gopher+
                # when it responds to info queries, each response line that
                # isn't a block header is indented by one space.
                data = re.sub("\n ", "\n", lines[1:].join("\n"))

                # Get the first space in the data.
                if self.verbose:
                    print("Data is %s" % data)

                # Watch out for the case when data is ''.  This could be in
                # particular if the server sends us a size packet like this:
                # +-1\r\n
                # Which would have a '' data segment.
                if data != '' and data[0] == ' ':
                    data = data[1:]

                # Assign it into the hash.
                if self.verbose:
                    print("Assigned data to key %s" % key)

                if data != '' and not data is None:
                    # No sense in assigning nothing into a key.  The getBlock()
                    # handles when there is no data and returns ''
                    self.blockdict[key] = data
            else:
                print("BLOCK ERROR: cannot find blockname in %s" % blocklabel)

        if self.verbose:
            k = list(self.blockdict.keys())
            print("Available block titles are:\n%s" % k.join("\n"))

        print("Keys are ", list(self.blockdict.keys()))
        return self

    # Simple accessors/mutators.
    # Sure, I could just monkey around with the data in an object from outside,
    # but in some cultures, people are executed for such offenses against the
    # OOP paradigm.  :)
    def setBlock(self, blockname, blockval):
        self.blockdict[blockname.lower()] = blockval
        return self.getBlock(blockname.lower())
    def setInfo(self, newinfo):
        self.blockdict['info'] = newinfo
        return self.getInfo()
    def setAdmin(self, newadmin):
        self.blockdict['admin'] = newadmin
        return self.getAdmin()
    def setViews(self, newviews):
        self.blockdict['views'] = newviews
        return self.getViews()
    def setAbstract(self, newabstract):
        self.blockdict['abstract'] = newabstract
        return self.getAbstract()
    def getAbstract(self):
        return self.blockdict['abstract']
    def getViews(self):
        return self.blockdict['views']
    def getInfo(self):
        return self.blockdict['info']
    def getAdmin(self):
        return self.blockdict['admin']
    def getBlockNames(self):
        return list(self.blockdict.keys())
    def getBlock(self, blockname):
        try:
            return self.blockdict[blockname.lower()]
        except KeyError:
            return ''

class GUIResourceInformation(Pmw.TextDialog):
    def __init__(self, resource_info_object):
        Pmw.TextDialog.__init__(self, title="Resource Information")
        self.insert('end', resource_info_object.toString())
        return None
    
        
