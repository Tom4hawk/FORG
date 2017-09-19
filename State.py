# State.py
# $Id: State.py,v 1.2 2001/07/11 22:43:09 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# Saves state information about a particular GopherResource.
# This is a bit overkill, but it was easier than putting the information
# in a tuple and then having to worry about which index gets to which item
# in the tuple.  Easier just to call methods like getResource()  :)
#
# This is just a souped up structure.  No calculation is done, just accessors
# and mutators are provided to bundle several different data items together
# under one object.
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
class State:
    verbose = None
    
    def __init__(self, response, resource, widget):
        self.response = response
        self.resource = resource
        self.widget   = widget
        return None
    
    def __str__(self):
        return "%s" % self.resource.toURL()
    
    def __repr__(self):
        return self.__str__()

    # Accessors
    
    def getResponse(self):
        return self.response
    
    def getResource(self):
        return self.resource
    
    def getWidget(self):
        return self.widget

    # Mutators
    
    def setResponse(self, resp):
        self.response = resp
        return self.getResponse()
    
    def setResource(self, res):
        self.resource = res
        return self.getResource()
    
    def setWidget(self, widget):
        self.widget = widget
        return self.getWidget()
