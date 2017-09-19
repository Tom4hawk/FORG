# ListNode.py
# $Id: ListNode.py,v 1.6 2001/07/11 22:43:09 s2mdalle Exp $
# Nodes to be placed in List objects.
# Subclass freely!  Life is short!
#
# Written by David Allen <mda@idatar.com>
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

class ListNode:
    def __init__(self, data=None, next=None, prev=None):
        self.next = next
        self.prev = prev
        self.data = data
        return None
    
    def __str__(self):
        return self.data.__str__
    
    def __repr__(self):
        return self.data.__repr__
    
    def getNext(self):
        """Return the next item in the list"""
        return self.next
    
    def getPrev(self):
        """Return the previous item in the list"""
        return self.prev
    
    def getData(self):
        """Return the data inside this object Node"""
        return self.data
    
    def setNext(self, newnext):
        """Set the next item in the list"""
        self.next = newnext
        return self.next
    
    def setPrev(self, newprev):
        """Set the previous item in the list"""
        self.prev = newprev
        return self.prev
    
    def setData(self, data):
        """Set the data inside the object."""
        self.data = data
        return self.data

