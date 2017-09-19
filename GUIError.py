# GUIError.py
# $Id: GUIError.py,v 1.3 2001/02/22 03:01:03 s2mdalle Exp $
#
# Displays errors similar to "Cannot Load Page" in the main window.
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
##########################################################################

from gopher import *
from Tkinter import *
import Pmw
from string import *

import GopherResource
import GopherResponse
import GopherConnection
import ContentFrame
import Cache
import Options

class GUIError(ContentFrame.ContentFrame, Frame):
    verbose = None

    def __init__(self, parent_widget, resource, error_message):
        Frame.__init__(self, parent_widget)
        ContentFrame.ContentFrame.__init__(self)
        self.parent = parent_widget

        Label(self, text="Unable to load").pack()
        Label(self, text=resource.toURL()).pack()
        Label(self, text=error_message).pack()
    def pack_content(self, *args):
        return None
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        self.parent.genericError("Error:  Error messages\n" +
                                 "are not searchable.")
        return None
