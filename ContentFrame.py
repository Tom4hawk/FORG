# ContentFrame.py
# $Id: ContentFrame.py,v 1.6 2001/03/27 22:18:02 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# This is the base class for anything that gets displayed by the program
# in the main window to represent a response from the server.  In other words,
# things such as text boxes and directory listings from gopher servers should
# extend this class.
#
# This class defines the behavior of anything that is presented to the user.
# OK, so I'm a bit new to python.  What I mean here is like a Java interface.
# I know I can't force subclasses to 'implement' this function, but they
# should, otherwise the functions here will spit out obscene messages to the
# user.  :)
#
# Note that creating the object is NOT ENOUGH.  You must call pack_content
# after creating it to actually add all the things that the widget will display
# this is a workaround for some odd behavior in Pmw.  For this reason you
# should NOT rely on nothing being present in the widget if you don't call
# pack_content.
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
###############################################################################

from tkinter import *
import Pmw

class ContentFrame:
    useStatusLabels = None
    
    def __init__(self):
        pass
    def pack_content(self, *args):
        """Packs the content of the box into the frame.  Note this does NOT
        pack this object into its parent, only its children into itself."""
        print("ContentFrame.pack_content:  Superclass failed to override.")
        return None
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        """Find some term within a frame.  If caseSensitive is true, then the
        search will be caseSensitive.  lastIdentifier is something that was
        previously returned by this function as the last match.  If you want
        to find the next occurance of something, pass the last occurance in
        and it will search from then on."""
        print("**********************************************************")
        print("***** ContentFrame.find():  Some subclass fucked up. *****")
        print("**********************************************************")
        return None
