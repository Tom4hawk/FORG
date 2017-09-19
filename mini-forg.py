#!/usr/bin/python
# Written by David Allen <mda@idatar.com>
# This is a proof of concept on how to embed the application.  Just using this
# code embeds the entire application minus a few niceties (like bookmarks, etc)
# into a popup window.
#
# This was just meant to display that the operation of the program is
# segregated from the operation of the main GUI, and how to embed the FORG
# in python/Tkinter programs.
#
# This file is released under the terms of the GNU General Public License.
##############################################################################

from Tkinter import *
import GopherResource
import forg

x = Tk()
r = GopherResource.GopherResource()
r.setURL("gopher://gopher.quux.org")
r.setName("QUUX.org")

# Create a FORG object.  You only have to tell it what your parent
# window is, and what resource it should load when it starts.
f = forg.FORG(parent_widget=x, resource=r)

# Pack it in
f.pack(fill='both', expand=1)

# Start the mini application.
x.mainloop()
