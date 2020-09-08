# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# This is the class that describes how files behave when loaded into
# the FORG.
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

from tkinter import *
from gopher import *
import Pmw
import re
import Options

import ContentFrame
import GopherResource
import GopherResponse

class GUIFile(ContentFrame.ContentFrame, Frame):
    verbose = None
    
    def __init__(self, parent_widget, parent_object, resp,
                 resource, filename):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.resp = resp

        if self.useStatusLabels:
            labeltext = "%s:%d" % (resource.getHost(), int(resource.getPort()))

            if resource.getName() != '' and resource.getLocator() != '':
                label2 = "\"%s\" ID %s" % (resource.getName(),
                                           resource.getLocator())
            else:
                label2 = "    "

            if len(label2) > 50:
                label2 = label2[0:47] + "..."

            Label(self, text=labeltext).pack(expand=0, fill='x')
            Label(self, text=label2).pack(expand=0, fill='x')

        if resp.getTypeCode() != RESPONSE_FILE:
            Label(self, text="This file has been saved in:").pack()
            Label(self, text=filename).pack()
        else:
            self.textwid = Pmw.ScrolledText(self, hscrollmode='dynamic',
                                            vscrollmode='static')
            tw = self.textwid.component('text')
            tw.configure(background='#FFFFFF', foreground='#000000')
                
            self.textwid.component('text').bind('<Button-3>',
                                                parent_object.popupMenu)
            
            self.textwid.pack(expand=1, fill='both')
        return None

    def pack_content(self, *args):
        if Options.program_options.getOption('strip_carraige_returns'):
            # print "Stripping carriage returns..."
            data = self.resp.getData().replace("\r", "")
        else:
            data = self.resp.getData()

        if len(data) < 1024:
            self.textwid.settext(data)
        else:
            for index in range(0, len(data), 500):
                self.textwid.insert('end', data[index:index+500])
        return None
    
    def destroy(self, *args):
        self.pack_forget()
        self.textwid.destroy()
        Frame.destroy(self)
        return None

    def find(self, term, caseSensitive=None, lastIdentifier=None):
        """Overrides the function of the same type from ContentFrame"""
        try:
            # This will raise an exception if it's a 'save' type layout
            # where the data isn't displayed to the user.
            tw = self.textwid.component('text')
            print("Component is ", tw)
        except:
            # Don't mess with this.  The user can read the entire label, all
            # big bad few lines of it.
            raise Exception("This window is not searchable.")

        if lastIdentifier is None:
            lastIdentifier = '0.0'

        # The variable caseSensitive is true if the search is case sensitive,
        # and false otherwise.  But since tkinter wants to know whether or not
        # the search is case INsensitive, we flip the boolean value, and use
        # it for the 'nocase' keyword arg to the search method.
        csflipped = (not caseSensitive)
        pos = tw.search(pattern=term, forwards=1,
                        nocase=csflipped, index=lastIdentifier,
                        stopindex=END)
        
        if pos:
            # Find the real index of the position returned.
            found_index = tw.index(pos)
        else:
            found_index = None

        print("Found index is \"%s\"" % found_index)

        if found_index:
            tw.yview(found_index)
            ending_index = tw.index("%s + %d chars" % (found_index, len(term)))
            # Set the selection to highlight the given word.
            tw.tag_add(SEL, found_index, ending_index)
            return tw.index("%s + 1 chars" % found_index)

        return None
