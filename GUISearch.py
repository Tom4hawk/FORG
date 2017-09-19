# GUISearch.py
# $Id: GUISearch.py,v 1.6 2001/04/15 19:27:00 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# Released under the terms of the GNU General Public License
#
# This is the graphical component used for getting information from the user
# about search terms.  (And then sending them on their merry way)
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

from Tkinter import *
from gopher import *
import Pmw
import ContentFrame
import GopherResource
import GopherResponse
import GopherConnection

class GUISearch(ContentFrame.ContentFrame, Frame):
    verbose = None
    
    def __init__(self, parent_widget, parent_object, resp,
                 resource, filename=None, menuAssocs={}):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.resource = resource
        self.response = resp
        self.parent   = parent_object
        self.filename = filename

        labels = ["Please enter a space-separated list of search terms."]

        last = 0
        
        for x in range(0, len(labels)):
            last = x
            label = labels[x]
            Label(self, text=label, foreground='#000000').grid(row=x, column=0,
                                                               columnspan=2)

        self.entryArea = Frame(self)
        self.entryArea.grid(row=(x+1), column=0, columnspan=5, sticky='EW')
        self.entryBox = Entry(self.entryArea, text='')
        self.entryBox.pack(side='left', expand=1, fill='x')
        self.entryBox.bind("<Return>", self.submit)
        self.GO = Button(self.entryArea, text='Submit', command=self.submit)
        self.GO.pack(side='right')
        self.bottom_label = None
        return None
    def pack_content(self, *args):
        return None
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        self.parent.genericError("Error:  Search boxes\n" +
                                 "are not searchable.")
        return None
    def submit(self, *args):
        terms = self.entryBox.get()

        print "Terms are \"%s\"" % terms

        if self.bottom_label:
            self.bottom_label.destroy()
            self.bottom_label = Label(self, "Searching for \"%s\"" % terms)
            self.bottom_label.grid(row=10, column=0, columnspan=2,
                                   sticky=W)

        # Copy the data from the current resource.
        res = GopherResource.GopherResource()
        res.setHost(self.resource.getHost())
        res.setPort(self.resource.getPort())
        res.setName(self.resource.getName())

        # This is a nasty way of faking the appropriate protocol message,
        # but oh well...
        res.setLocator("%s\t%s" % (self.resource.getLocator(),
                                   terms))
        res.setInfo(None)
        res.setLen(-2)
        res.setTypeCode(RESPONSE_DIR)   # Response *will* be a directory.

        self.parent.goElsewhere(res)
        return None
    

