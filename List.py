# List.py
# $Id: List.py,v 1.8 2001/08/12 20:40:14 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# This is a data structure similar to a doubly linked list, but with a few
# exceptions - it has to keep track of all nodes that have EVER been in the
# list, to cache old nodes for jumping around.  It also has to know that when
# you insert a completely new item, it removes everything after the current
# slot in the list.  This is because when you jump to a new document like in
# a web browser, you can't then hit the 'forward' button.
#
# The forward and back buttons in the program will correspond to methods in
# this object.
#
# Only put ListNode objects into this.
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

from ListNode import *

ListException = "List error"

class List:
    def __init__(self):
        self.front   = ListNode()
        self.back    = ListNode()
        self.front.setNext(self.back)
        self.front.setPrev(None)
        self.back.setPrev(self.front)
        self.back.setNext(None)
        self.current = self.front
        return None

    def goToFront(self):
        """Sets the current node to the first node in the list."""
        self.current = self.front.next
        return None

    def goToBack(self):
        """Sets the current node to the last node in the list."""
        self.current = self.back.prev
        return None
        
    def atEnd(self):
        """Predicate:  Returns true if the current item is the last item in
        the list."""
        return self.current == self.back
    
    def atFront(self):
        """Predicate:  Returns true if the current item is the first item in
        the list."""
        return self.current == self.front
    
    def itemsRemaining(self):
        """Predicate:  Returns true if the current item is not the last
        item"""
        return not self.atEnd()
    
    def isEmpty(self):
        """Predicate:  Returns true if the list contains > 0 items."""
        if self.front.getNext() == self.back:
            return 1
        else:
            return None
        
    def traverse(self, function):
        """Takes a function argument, returns a list which contains the result
        of applying the function to each item in the list successivly.  Sort
        of like map() for this list particularly."""
        n = self.front.getNext()
        listresults = [] 
        while n != self.back:
            listresults.append(function(n))
            n = n.getNext()
        return listresults

    def insertAfter(self, newnode, afterWhat):
        """Inserts newnode after afterWhat.  afterWhat may actually be either
        a ListNode in the list, or it may be the data inside a particular
        ListNode.  But it must be a reference to the *same* data, (or node)
        not a reference to equivalent data (or node)."""
        
        n = self.front.getNext()

        if newnode.__class__ != ListNode:
            raise ListException, "newnode argument must be a ListNode"

        while n != self.back.getPrev():
            if afterWhat == n or afterWhat == n.getData():
                nn = n.getNext()
                newnode.setPrev(n)
                newnode.setNext(nn)
                afterWhat.setNext(newnode)
                nn.setPrev(newnode)
                return newnode

            n = n.getNext()

        raise ListException, "cannot insert after nonexistent node."

    def removeReference(self, ref):
        """Removes ref from the list.  Note this must be a reference to
        something in the list, not just something that has the same data."""

        n = self.front.getNext()
        
        while n != self.back:
            # We're going to be very forgiving and let the user pass us a
            # reference to either the data contained in the ListNode object,
            # or a reference to the ListNode object itself.
            if n == ref or n.getData() == ref:
                np = n.getPrev()
                nn = n.getNext()
                n.setNext(None)      # Kill the links on the node we delete...
                n.setPrev(None)
                np.setNext(nn)       # Update the links on the surrounding
                nn.setPrev(np)       # nodes...
                return ref           # Get out...we only remove the 1st one.
            
            n = n.getNext()          # Next item in the list.
            
        raise ListException, "Reference not found in list"
        
    def countNodes(self, f=None):
        """Returns the number of nodes in the list."""
        if f is None:
            f = self.front
        nodes = 0
        n = f.getNext()
        while n != self.back:
            nodes = nodes + 1
            n = n.getNext()
        return nodes
    
    def prepend(self, node):
        """Inserts the given node at the front of the list."""
        self.current = self.front
        return self.insert(node, truncate=0)
    
    def postpend(self, node):
        """Inserts the given node at the very back of the list."""
        self.current = self.back.getPrev()
        return self.insert(node, 0)
    
    def insert(self, node, truncate=1):
        """Inserts node as the next item in the list.  If truncate is true,
        then all subsequent elements are dropped, and the new node becomes
        the last node in the list."""
        if truncate:
            node.setPrev(self.current)
            node.setNext(self.back)
            self.current.setNext(node)
            self.current = node
            return self.current
        else:
            oldnext = self.current.getNext()
            node.setPrev(self.current)
            node.setNext(oldnext)
            self.current.setNext(node)
            oldnext.setPrev(node)
            self.current = node
            return self.current

    def getCurrent(self):
        """Returns the current node."""
        return self.current
    
    def removeCurrent(self):
        """Removes the current node.  The current node then becomes the next
        node in the list."""
        if not self.current:
            raise ListException, "Error:  Cannot delete NONE"
        if self.current == self.front:
            raise ListException, "Cannot delete FRONT"
        if self.current == self.back:
            raise ListException, "Cannot delete BACK"
        
        one_before_this_one = self.current.getPrev()
        one_after_this_one  = self.current.getNext()
        one_before_this_one.setNext(one_after_this_one)
        one_after_this_one.setPrev(one_before_this_one)
        self.current.setPrev(None)
        self.current.setNext(None)
        self.current.setData(None)
        self.current = one_after_this_one
        return self.current

    def getFirst(self):
        """Returns the first item in the list.  Does not change the current
        node"""
        
        first = self.front.next

        if first == self.back:
            raise ListException, "The list is empty"
        return first

    def getLast(self):
        """Returns the last item in the list.  Does not change the current
        node"""
        last = self.back.prev

        if last == self.front:
            raise ListException, "The list is empty"
        return last
    
    def getNext(self):
        """Returns the next node in the list, and advances the current node."""
        next = self.current.getNext()
        
        if next == self.back or (next == None and next == self.back):
            raise ListException, "Already at the end of the list"
        elif next == None:
            raise ListException, "getNext(): Null next field"
        
        self.current = next
        return self.current
    
    def getPrev(self):
        """Returns the previous node in the list, which then becomes the
        current node."""
        prev = self.current.getPrev()
        
        if prev == self.front or (prev == None and prev == self.front):
            raise ListException, "Already at the beginning of the list"
        elif prev == None:
            raise ListException, "getPrev(): Null prev field."

        self.current = self.current.getPrev()
        return self.current

# EOF
