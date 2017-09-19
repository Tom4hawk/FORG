# Tree.py
# highly optimized tkinter tree control
# Written by Charles E. "Gene" Cash <gcash@fdn.com>
# Modifications by David Allen <mda@idatar.com>
#
# 98/12/02 CEC started
# 99/??/?? CEC release to comp.lang.python.announce
#
# to do:
# add working "busy" cursor
# make paste more general
# add good ideas from win95's tree common control
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
            
import os
import string
import Tkdnd
import Bookmark
import ListNode
import List
import BookmarkEditor
import Dialogs
from Tkinter import *

# this is initialized later, after Tkinter is started
class Icons:
    OPEN_ICON = None
    SHUT_ICON = None
    FILE_ICON = None

#------------------------------------------------------------------------------
# cut'n'paste helper object

class Cut_Object:
    def __init__(self, node=None, id=None, state=None):
        self.node    = node
        self.full_id = id
        self.state   = state
    def getNode(self):
        return node
    def getFullId(self):
        return self.full_id
    def getState(self):
        return state
        
#------------------------------------------------------------------------------
# tree node helper class

class NodeData:
    """This is the same as Node, but only holds the data and does nothing with
    it.  This is ideal for creating nodes that you don't want drawn until they
    get pasted in via a Cut_Object"""
    def __init__(self, parent, name, id, closed_icon, open_icon, x, y,
                 parentwidget):
        self.parent      = parent
        self.name        = name
        self.id          = id
        self.open_icon   = open_icon
        self.closed_icon = closed_icon
        self.widget      = parentwidget
        self.subnodes    = []
        self.spinlock    = 0
        self.openflag    = 0
        return None
    
class Node:
    # initialization creates node, draws it, and binds mouseclicks
    def __init__(self, parent, name, id, closed_icon, open_icon, x, y,
                 parentwidget):
        # lots of things to remember
        # immediate parent node
        self.parent = parent

        self.__x = x
        self.__y = y
        
        # name displayed on the label
        self.name = name
        
        # internal name used to manipulate things
        self.id = id
        
        # bitmaps to be displayed
        self.open_icon   = open_icon
        self.closed_icon = closed_icon
        
        # tree widget we belong to
        self.widget = parentwidget
        
        # our list of child nodes
        self.subnodes = []
        
        # cheap mutex spinlock
        self.spinlock = 0
        # closed to start with
        self.open_flag = 0
            
        # call customization hook
        if self.widget.init_hook:
            self.widget.init_hook(self)

    def drawNode(self):
        # draw horizontal connecting lines
        if self.widget.lineflag:
            self.line = self.widget.create_line(self.__x-self.widget.distx,
                                                self.__y, self.__x, self.__y)

        # draw approprate image
        self.symbol = self.widget.create_image(self.__x, self.__y,
                                               image=self.closed_icon)

        # add label
        self.label = self.widget.create_text(self.__x+self.widget.textoff,
                                             self.__y, 
                                             text=self.name, justify='left',
                                             anchor='w')

        def infoCallback(event, s=self):
            display_information(s, s.widget)
        
        self.widget.tag_bind(self.label, '<Double-Button-1>', infoCallback)

        # single-click to expand/collapse
        cmd = self.widget.tag_bind(self.symbol, '<1>', self.click)
            
        # drag'n'drop support
        if self.widget.dnd_hook:
            # this starts the drag operation
            self.widget.tag_bind(self.label, '<1>',
                                 lambda ev,
                                 qs=self:qs.widget.dnd_click(ev, qs))

            # these events help identify drop target node
            self.widget.tag_bind(self.symbol, '<Enter>',
                                 lambda ev, qs=self:qs.widget.enter(qs))
            self.widget.tag_bind(self.label, '<Enter>',
                                 lambda ev, qs=self:qs.widget.enter(qs))
            self.widget.tag_bind(self.symbol, '<Leave>', self.widget.leave)
            self.widget.tag_bind(self.label, '<Leave>', self.widget.leave)
        elif self.widget.item_dbl_click_hook:
            self.widget.tag_bind(self.label, '<Double-Button-1>',
                                 self.widget.item_dbl_click_hook)

    def isFile(self):
        return (self.children() == 0 and
                (self.open_icon == None or self.open_icon == Icons.FILE_ICON))

    def isFolder(self):
        return not self.isFile()

    def children(self):
        return len(self.subnodes)

    def __repr__(self):
        try:
            # Parent may be None so this may croak.
            pname = self.parent.name 
        except:
            pname = "NONEXISTANT"
            
        return 'Node: %s  Parent: %s  (%d children)' % \
               (self.name, pname, len(self.subnodes))
    
    # recursively delete subtree & clean up cyclic references
    def _delete(self):
        for i in self.subnodes:
            if i.open_flag and i.subnodes:
                # delete vertical connecting line
                if self.widget.lineflag:
                    self.widget.delete(i.tree)

            # delete node's subtree, if any
            i._delete()

            # the following unbinding hassle is because tkinter
            # keeps a callback reference for each binding
            # so if we want things GC'd...
            #
            # MDA: 7/5/2001: Commented this out because it breaks with
            # Python 2.1's default Tkinter as _tagcommands doesn't exist.
            # Followup.
            # for j in (i.symbol, i.label):
            #    for k in self.widget.tag_bind(j):
            #        self.widget.tag_unbind(j, k)
            #    for k in self.widget._tagcommands.get(j, []):
            #        self.widget.deletecommand(k)
            #        self.widget._tagcommands[j].remove(k)
                    
            # delete widgets from canvas
            self.widget.delete(i.symbol, i.label)
            if self.widget.lineflag:
                self.widget.delete(i.line)
                
            # break cyclic reference
            i.parent=None

        # move cursor if it's in deleted subtree
        if self.widget.pos in self.subnodes:
            self.widget.move_cursor(self)
            
        # now subnodes will be properly garbage collected
        self.subnodes = []

    # move everything below current icon, to make room for subtree
    # using the magic of item tags
    def _tagmove(self, dist):
        # mark everything below current node as movable
        bbox1 = self.widget.bbox(self.widget.root.symbol, self.label)
        bbox2 = self.widget.bbox('all')
        self.widget.dtag('move')
        self.widget.addtag('move', 'overlapping', 
                           bbox2[0], bbox1[3], bbox2[2], bbox2[3])

        # untag cursor & node so they don't get moved too
        # this has to be done under Tk on X11
        self.widget.dtag(self.widget.cursor_box, 'move')
        self.widget.dtag(self.symbol, 'move')
        self.widget.dtag(self.label, 'move')

        # now do the move of all the tagged objects
        self.widget.move('move', 0, dist)

        # fix up connecting lines
        if self.widget.lineflag:
            n = self
            while n:
                if len(n.subnodes) and n.subnodes[-1] is not None:
                    # position of current icon
                    x1, y1 = self.widget.coords(n.symbol)
                    # position of last node in subtree
                    x2, y2 = self.widget.coords(n.subnodes[-1:][0].symbol)
                    self.widget.coords(n.tree, x1, y1, x1, y2)
                n = n.parent

    # return list of subnodes that are expanded (not including self)
    # only includes unique leaf nodes (e.g. /home and /home/root won't
    # both be included) so expand() doesn't get called unnecessarily
    # thank $DEITY for Dr. Dutton's Data Structures classes at UCF!
    def expanded(self):
        # push initial node into stack
        stack = [(self, (self.id,))]
        list = []
        while stack:
            # pop from stack
            p, i = stack[-1:][0]
            del stack[-1:]
            # flag to discard non-unique sub paths
            flag = 1
            # check all children
            for n in p.subnodes:
                # if expanded, push onto stack
                if n.open_flag:
                    flag = 0
                    stack.append(n, i+(n.id,))
            # if we reached end of path, add to list
            if flag:
                list.append(i[1:])
        return list

    # get full name, including names of all parents
    def full_id(self):
        if self.parent:
            return self.parent.full_id()+(self.id,)
        else:
            return (self.id,)

    # expanding/collapsing folders
    def toggle_state(self, state=None):
        if not self.open_icon:
            # not a expandable folder
            return
        if state == None:
            # toggle to other state
            state = not self.open_flag
        else:
            # are we already in the state we want to be?
            if (not state) == (not self.open_flag):
                return

        # not re-entrant
        # acquire mutex
        while self.spinlock:
            pass
        self.spinlock = 1
        
        # call customization hook
        if self.widget.before_hook:
            self.widget.before_hook(self)

        # if we're closed, expand & draw our subtrees
        if not self.open_flag:
            self.open_flag = 1
            self.widget.itemconfig(self.symbol, image=self.open_icon)

            # get contents of subdirectory or whatever
            contents = self.widget.get_contents(self)

            # move stuff to make room
            self._tagmove(self.widget.disty*len(contents))

            # now draw subtree
            self.subnodes = []
            
            # get current position of icon
            x, y = self.widget.coords(self.symbol)
            yp = y
            
            for i in contents:
                try:
                    print "CONTENTS: i is %s class %s" % (i, i.__class__)
                except:
                    pass
                # add new subnodes, they'll draw themselves
                yp = yp+self.widget.disty
                newnode = Node(self, i[0], i[1], i[2], i[3],
                               x+self.widget.distx, yp,
                               self.widget)
                newnode.drawNode()
                self.subnodes.append(newnode)
                
            # the vertical line spanning the subtree
            if self.subnodes and self.widget.lineflag:
                _tval = y+self.widget.disty*len(self.subnodes)
                self.tree = self.widget.create_line(x, y, x, _tval)
                self.widget.lower(self.tree, self.symbol)

        # if we're open, collapse and delete subtrees
        elif self.open_flag:
            self.open_flag = 0
            self.widget.itemconfig(self.symbol, image=self.closed_icon)

            # if we have any children
            if self.subnodes:
                # recursively delete subtree icons
                self._delete()

                # delete vertical line
                if self.widget.lineflag:
                    self.widget.delete(self.tree)

                # find next (vertically-speaking) node
                n = self
                while n.parent:
                    # position of next sibling in parent's list
                    i = n.parent.subnodes.index(n)+1
                    if i < len(n.parent.subnodes):
                        n = n.parent.subnodes[i]
                        break
                    n = n.parent
                    
                if n.parent:
                    # move everything up so that distance to next subnode is
                    # correct
                    x1, y1 = self.widget.coords(self.symbol)
                    x2, y2 = self.widget.coords(n.symbol)
                    dist = y2-y1-self.widget.disty
                    self._tagmove(-dist)

        # update scroll region for new size
        x1, y1, x2, y2 = self.widget.bbox('all')
        self.widget.configure(scrollregion=(x1, y1, x2+5, y2+5))

        # call customization hook
        if self.widget.after_hook:
            self.widget.after_hook(self)

        # release mutex
        self.spinlock = 0

    def expandAll(self):
        self.toggle_state(1) # Expand this item
        
        for n in self.subnodes:
            # Recursively expand subnodes.
            n.expandAll()
            
        return None

    # expand this subnode
    # doesn't have to exist, it expands what part of the path DOES exist
    def expand(self, dirs):
        # if collapsed, then expand
        self.toggle_state(1)

        # find next subnode
        if dirs:
            for n in self.subnodes:
                if n.id == dirs[0]:
                    n.expand(dirs[1:])
                    break
    
    # handle mouse clicks by moving cursor and toggling folder state
    def click(self, event):
        self.widget.move_cursor(self)
        self.toggle_state()

    # cut a node and it's subtree
    def cut(self):
        # remember what was expanded, so we can re-expand on paste
        expand_list = self.expanded()
        if not self.open_flag:
            expand_list = None

        id = self.full_id()
        
        # collapse
        self.toggle_state(0)

        # delete from tree
        if self.parent:
            # Remove all data from the parent's BookmarkMenu
            # print "Removing reference from \"%s\" to \"%s\"" % (
            #     self.parent.id, self.id)
            # print "Class of removee is ", self.id.__class__
            self.parent.id.removeReference(self.id)
            
            # move cursor safely out of the way
            if self.widget.pos == self:
                self.widget.prev()
                
            if len(self.parent.subnodes) == 1:
                # delete vertical connecting line
                # if we're the only child
                if self.widget.lineflag:
                    self.widget.delete(self.parent.tree)

            # delete from parent's list of children
            self.parent.subnodes.remove(self)

        # move rest of tree up
        self._tagmove(-self.widget.disty)

        # break cyclic reference
        self.parent = None

        # see _delete() for why we have to do this
        # MDA: 7/5/2001: Commented this out because it breaks with
        # Python 2.1's default Tkinter as _tagcommands doesn't exist.
        # Followup.
        # for j in (self.symbol, self.label):
        #    for k in self.widget.tag_bind(j):
        #         self.widget.tag_unbind(j, k)
        #     for k in self.widget._tagcommands.get(j, []):
        #         self.widget.deletecommand(k)
        #         self.widget._tagcommands[j].remove(k)
                
        # delete from canvas
        self.widget.delete(self.symbol, self.label)
        if self.widget.lineflag:
            self.widget.delete(self.line)
            
        # update scrollbar for new height
        x1, y1, x2, y2 = self.widget.bbox('all')
        self.widget.configure(scrollregion=(x1, y1, x2+5, y2+5))

        # returns a "cut_object"
        co = Cut_Object(self, id, expand_list)
        
        # call customization hook
        if self.widget.cut_hook:
            self.widget.cut_hook(co)

        return co

    # insert a "cut object" at the proper place
    # option:
    # 1 - insert as 1st child
    # 2 - insert after last child
    # 3 - insert as next sibling
    def paste(self, co, option=1):
        # call customization hook
        # this usually does the actual cut'n'paste on the underlying
        # data structure
        if self.widget.paste_hook:
            # if it returns false, it wasn't successful
            if self.widget.paste_hook(co):
                return

        self.expand([1])
        # expand if necessary
        # if option == 1 or option == 2:
        #     self.toggle_state(2)

        # Uncomment if lineflag to Tree() was true.
        #if option == 1 or option == 2 and not self.subnodes:
        #    # Create the horizontal line if it isn't already present.
        #    # (i.e. inserting into a dir that has 0 children)
        #    # Warning: this is an ugly hack.
        #    x, y = self.widget.coords(self.symbol)
        #    _tval = y+self.widget.disty*len(self.subnodes)
        #    self.tree = self.widget.create_line(x, y, x, _tval)
        #    self.widget.lower(self.tree, self.symbol)
            
        # make subnode list the right size for _tagmove()
        if option == 1 or not self.parent:
            self.subnodes.insert(0, None)
            # Option is insert as first child, so prepend the Bookmark
            # to the BookmarkMenu
            self.id.prepend(ListNode.ListNode(co.node.id))
            i = 0
        elif option == 2:
            self.id.postpend(ListNode.ListNode(co.node.id))
            self.subnodes.append(None)
            i = -1
        elif option == 3:
            i = self.parent.subnodes.index(self)+1

            # Update the BookmarkMenu relationship
            self.parent.id.insertAfter(newnode=ListNode.ListNode(co.node.id),
                                       afterWhat=self.id)

            # Update the list of GUI subnodes
            self.parent.subnodes.insert(i, None)
            
        # move rest of tree down
        self._tagmove(self.widget.disty)

        # place new node
        xval, yval = self.widget.coords(self.symbol)
        if option == 1 or option == 2:
            xval = xval+self.widget.distx
        yval = yval+self.widget.disty

        # create node
        if option == 1 or option == 2:
            node_parent = self
        elif option == 3:
            node_parent = self.parent

        n = Node(parent=node_parent,
                 name=co.node.name,
                 id=co.node.id,
                 # co.node.open_flag,
                 # co.node.icon,
                 closed_icon=co.node.closed_icon,
                 open_icon=co.node.open_icon,
                 x=xval,
                 y=yval,
                 parentwidget=self.widget)
        n.drawNode()
        
        # insert into tree...if it's the root item, don't try to insert it as
        # a sibling.
        if option == 1 or option == 2 or not self.parent:
            self.subnodes[i] = n
        elif option == 3:
            # insert as next sibling
            self.parent.subnodes[i] = n
        
        # expand children to the same state as original cut tree
        if co.state:
            n.expand(co.state)

    # return next lower visible node
    def next(self):
        n = self
        if n.subnodes:
            # if you can go right, do so
            return n.subnodes[0]
        while n.parent:
            # move to next sibling
            i = n.parent.subnodes.index(n)+1
            if i < len(n.parent.subnodes):
                return n.parent.subnodes[i]
            # if no siblings, move to parent's sibling
            n = n.parent
        # we're at bottom
        return self
    
    # return next higher visible node
    def prev(self):
        n = self
        if n.parent:
            # move to previous sibling
            i = n.parent.subnodes.index(n)-1
            if i >= 0:
                # move to last child
                n = n.parent.subnodes[i]
                while n.subnodes:
                    n = n.subnodes[-1]
            else:
                # punt if there's no previous sibling
                if n.parent:
                    n = n.parent
        return n

def display_information(node, parent_widget):
    """Displays information about the given node in a separate window that
    is a child of parent_widget.  This is for when the user requests
    information about different tree items."""
    data = node.id

    # Since python does everything call by reference, we can create a callback
    # function that merely edits the data of the node in place, and it will
    # apply to what's actually in the tree.
    # Pass this the original reference (in the tree) and the new resource
    # whose information matches what the stuff in the tree should be.
    def editReference(orig_reference, new_res, n=node):
        if orig_reference.__class__ == Bookmark.Bookmark:
            orig_reference.setURL(new_res.getURL())
            orig_reference.setName(new_res.getName())
            # Update the label on the widget
            n.widget.itemconfig(n.label, text=new_res.getName())
        else:
            # It's a folder.
            orig_reference.setName(new_res)
            n.widget.itemconfig(n.label, text=new_res)

        return None

    # Ugly.  NewBookmarkDialog takes a callback, and this is it.  It will
    # pass the res argument - a newly created GopherResource object.
    # Call editReference on it instead with the required arguments.
    def editReferenceStub(res, ref=data, callback=editReference):
        return callback(orig_reference=ref,
                        new_res=res)

    if data.__class__ == Bookmark.Bookmark:
        # Create a new bookmark dialog.  Note this is the same that is used to
        # create new bookmarks, we're just specifying the callback to actually
        # change an existing one instead of create something new in the tree.
        e = Dialogs.NewBookmarkDialog(parent_widget,
                                      editReferenceStub, data)
    else:
        # Same as above (for bookmark dialogs) except this is for folder
        # names.
        e = Dialogs.NewFolderDialog(parent_widget,
                                    editReferenceStub, data.getName())
    return None

#------------------------------------------------------------------------------
# default routine to get contents of subtree
# supply this for a different type of app
# argument is the node object being expanded
# should return list of 4-tuples in the form:
# (label, unique identifier, closed icon, open icon)
# where:
#    label             - the name to be displayed
#    unique identifier - an internal fully unique name
#    closed icon       - PhotoImage of closed item
#    open icon         - PhotoImage of open item, or None if not openable
def get_contents(node):
    """Returns the contents of a particular node"""

    def fn(node):
        """Just a function used for traversing the list inside of a
        BookmarkMenu object.  See Bookmark.BookmarkMenu for information on
        how they are put together"""
        node = node.getData()
        if node.__class__ == Bookmark.BookmarkMenu:
            node_name = node.getName()
            tuple = (node_name, node, Icons.SHUT_ICON, Icons.OPEN_ICON)
        else:
            node_name = node.getName()
            tuple = (node_name, node, Icons.FILE_ICON, None)

        return tuple
    
    if node.id.__class__ == Bookmark.BookmarkMenu:
        l = node.id.traverse(fn)
        return l
    else:   # It's a Bookmark.ListItem object
        tuple = (node.id.getData().getName(), node.id.getData(),
                 Icons.FILE_ICON, None)
        return tuple
                
#------------------------------------------------------------------------------
class Tree(Canvas):
    def __init__(self, master, datatree, rootlabel=None,
                 openicon=None, shuticon=None, getcontents=get_contents,
                 init=None, before=None, after=None, cut=None, paste=None,
                 dnd=None, distx=15, disty=15, textoff=10, lineflag=1,
                 **kw_args):
        self.data_tree = datatree
        self.cutbuffer = None
        
        # pass args to superclass
        apply(Canvas.__init__, (self, master), kw_args)
        
        # default images (BASE64-encoded GIF files)
        # we have to delay initialization until Tk starts up or PhotoImage()
        # complains (otherwise I'd just put it up top)
        if Icons.OPEN_ICON == None:
            Icons.OPEN_ICON = PhotoImage(
                data='R0lGODlhEAANAKIAAAAAAMDAwICAgP//////ADAwMAAAAAAA' \
                'ACH5BAEAAAEALAAAAAAQAA0AAAM6GCrM+jCIQamIbw6ybXNSx3GVB' \
                'YRiygnA534Eq5UlO8jUqLYsquuy0+SXap1CxBHr+HoBjoGndDpNAAA7')
            Icons.SHUT_ICON = PhotoImage(
                data='R0lGODlhDwANAKIAAAAAAMDAwICAgP//////ADAwMAAAAAAA' \
                'ACH5BAEAAAEALAAAAAAPAA0AAAMyGCHM+lAMMoeAT9Jtm5NDKI4Wo' \
                'FXcJphhipanq7Kvu8b1dLc5tcuom2foAQQAyKRSmQAAOw==')
            Icons.FILE_ICON = PhotoImage(
                data='R0lGODlhCwAOAJEAAAAAAICAgP///8DAwCH5BAEAAAMALAAA' \
                'AAALAA4AAAIphA+jA+JuVgtUtMQePJlWCgSN9oSTV5lkKQpo2q5W+' \
                'wbzuJrIHgw1WgAAOw==')
            
        # function to return subnodes (not very much use w/o this)
        if not getcontents:
            raise ValueError, 'must have "get_contents" function'
        
        self.get_contents = getcontents
        
        # horizontal distance that subtrees are indented
        self.distx = distx
        
        # vertical distance between rows
        self.disty = disty
        
        # how far to offset text label
        self.textoff = textoff

        # self.item_dbl_click_hook = self.editNode
        self.item_dbl_click_hook = None
        
        # called after new node initialization
        self.init_hook = init
        
        # called just before subtree expand/collapse
        self.before_hook = before
        
        # called just after subtree expand/collapse
        self.after_hook = after
        
        # called at the end of the cut operation
        self.cut_hook = cut
        
        # called beginning of the paste operation
        self.paste_hook = paste
        
        # flag to display lines
        self.lineflag = lineflag
        
        # called at end of drag'n'drop operation
        # self.dnd_hook = dnd
        self.dnd_hook = None
        
        # create root node to get the ball rolling
        if openicon:
            oi = openicon
        else:
            oi = Icons.OPEN_ICON
        if shuticon:
            si = shuticon
        else:
            si = Icons.SHUT_ICON

        if not rootlabel:
            rootlabel = " "

        self.root = Node(parent=None,
                         name=rootlabel,
                         id=self.data_tree,
                         closed_icon=si,
                         open_icon=oi,
                         x=10,
                         y=10,
                         parentwidget=self)
        
        self.root.drawNode()

        # configure for scrollbar(s)
        x1, y1, x2, y2 = self.bbox('all') 
        self.configure(scrollregion=(x1, y1, x2+5, y2+5))

        # add a cursor
        self.cursor_box = self.create_rectangle(0, 0, 0, 0)
        self.move_cursor(self.root)

        # make it easy to point to control
        self.bind('<Enter>', self.mousefocus)

        # totally arbitrary yet hopefully intuitive default keybindings
        # page-up/page-down
        self.bind('<Next>', self.pagedown)
        self.bind('<Prior>', self.pageup)

        # arrow-up/arrow-down
        self.bind('<Down>', self.next)
        self.bind('<Up>', self.prev)

        # arrow-left/arrow-right
        self.bind('<Left>', self.ascend)
        # (hold this down and you expand the entire tree)
        self.bind('<Right>', self.descend)

        # home/end
        self.bind('<Home>', self.first)
        self.bind('<End>', self.last)

        # space bar
        self.bind('<Key-space>', self.toggle)

    def destroy(self, *args):
        # Garbage collect the image objects.  If this isn't done,
        # Tkinter holds onto a useless reference to them which can cause
        # a stderr message.
        Icons.OPEN_ICON = None
        Icons.SHUT_ICON = None
        Icons.FILE_ICON = None

        # Superclass destructor
        Canvas.destroy(self)
        return None

    def editNode(self, node):
        pass

    # scroll (in a series of nudges) so items are visible
    def see(self, *items):
        x1, y1, x2, y2 = apply(self.bbox, items)
        while x2 > self.canvasx(0)+self.winfo_width():
            old = self.canvasx(0)
            self.xview('scroll', 1, 'units')
            # avoid endless loop if we can't scroll
            if old == self.canvasx(0):
                break
        while y2 > self.canvasy(0)+self.winfo_height():
            old = self.canvasy(0)
            self.yview('scroll', 1, 'units')
            if old == self.canvasy(0):
                break
        # done in this order to ensure upper-left of object is visible
        while x1 < self.canvasx(0):
            old = self.canvasx(0)
            self.xview('scroll', -1, 'units')
            if old == self.canvasx(0):
                break
        while y1 < self.canvasy(0):
            old = self.canvasy(0)
            self.yview('scroll', -1, 'units')
            if old == self.canvasy(0):
                break
            
    # move cursor to node
    def move_cursor(self, node):
        self.pos = node
        x1, y1, x2, y2 = self.bbox(node.symbol, node.label)
        self.coords(self.cursor_box, x1-1, y1-1, x2+1, y2+1)
        self.see(node.symbol, node.label)
    
    # expand given path
    # note that the convention used in this program to identify a
    # particular node is to give a tuple listing it's id and parent ids
    def expand(self, path):
        self.root.expand(path[1:])

    def setCutBuffer(self, newcutbuffer):
        self.cutbuffer = newcutbuffer
        return self.cutbuffer
    
    def getCutBuffer(self):
        return self.cutbuffer

    def getRoot(self):
        return self.root

    def cut(self):
        """Tree.cut: cut the selected node"""
        active = self.getActive()

        if active != self.root:     # Don't allow the user to cut the root node
            self.cutbuffer = self.getActive().cut()
        return None

    def expandAll(self):
        return self.root.expandAll()

    def paste(self):
        if self.cutbuffer:
            if self.getActive().isFolder() and self.cutbuffer.node.isFolder():
                # If we're pasting a folder into a folder, make it the
                # first item in the list
                self.getActive().paste(self.cutbuffer, 1)
            elif self.getActive().isFolder():
                # If we're pasting a non-folder into a folder, make it the
                # last sibling
                self.getActive().paste(self.cutbuffer, 2)
            else:
                # Otherwise, add the new item as the next sibling of whatever
                # was active.
                self.getActive().paste(self.cutbuffer, 3)
        return None

    def setActive(self, newactive):
        self.pos = newactive
        return self.pos

    def getActive(self):
        return self.pos

    def getTree(self):
        return self.root

    # soak up event argument when moused-over
    # could've used lambda but didn't...
    def mousefocus(self, event):
        self.focus_set()
        
    # open/close subtree
    def toggle(self, event=None):
        self.pos.toggle_state()

    # move to next lower visible node
    def next(self, event=None):
        self.move_cursor(self.pos.next())
            
    # move to next higher visible node
    def prev(self, event=None):
        self.move_cursor(self.pos.prev())

    # move to immediate parent
    def ascend(self, event=None):
        if self.pos.parent:
            # move to parent
            self.move_cursor(self.pos.parent)

    # move right, expanding as we go
    def descend(self, event=None):
        self.pos.toggle_state(1)
        if self.pos.subnodes:
            # move to first subnode
            self.move_cursor(self.pos.subnodes[0])
        else:
            # if no subnodes, move to next sibling
            self.next()

    # go to root
    def first(self, event=None):
        # move to root node
        self.move_cursor(self.root)

    # go to last visible node
    def last(self, event=None):
        # move to bottom-most node
        n = self.root
        while n.subnodes:
            n = n.subnodes[-1]
        self.move_cursor(n)

    # previous page
    def pageup(self, event=None):
        n = self.pos
        j = self.winfo_height()/self.disty
        for i in range(j-3):
            n = n.prev()
        self.yview('scroll', -1, 'pages')
        self.move_cursor(n)

    # next page
    def pagedown(self, event=None):
        n = self.pos
        j = self.winfo_height()/self.disty
        for i in range(j-3):
            n = n.next()
        self.yview('scroll', 1, 'pages')
        self.move_cursor(n)

    # drag'n'drop support using Tkdnd
    # start drag'n'drop
    def dnd_click(self, event, node):
        Tkdnd.dnd_start(self, event)
        self.dnd_source = node

    # remember node we just entered, and save it as target
    def enter(self, node):
        self.dnd_target = node

    # we're not over a valid target
    def leave(self, event):
        self.dnd_target = None
        
    # end drag'n'drop
    def dnd_end(self, target, event):
        pass
    
    def dnd_accept(self, source, event):
        return self

    def dnd_commit(self, source, event):
        # destroy the move icon
        self.dnd_leave(None, None)
        # force update to get <Enter> event, if any
        self.update()
        # see if non-trivial drag'n'drop occurred
        if self.dnd_target == None or source.dnd_source == self.dnd_target:
            return
        self.dnd_hook(source, self.dnd_target)

    # create drag icon
    def dnd_enter(self, source, event):
        # returns pointer position in display coordinates
        x, y = self.winfo_pointerxy()
        # translate to canvas coordinates
        x = self.canvasx(x)-self.winfo_rootx()
        y = self.canvasy(y)-self.winfo_rooty()
        i = source.itemcget(source.dnd_source.symbol, 'image')
        self.dnd_symbol = self.create_image(x, y, image=i)
        i = source.itemcget(source.dnd_source.label, 'text')
        self.dnd_label = self.create_text(x+self.textoff, y, 
                                          text=i, justify='left',
                                          anchor='w' )
                                             
    # destroy drag icon
    def dnd_leave(self, source, event):
        self.delete(self.dnd_symbol, self.dnd_label)

    # move drag icon
    def dnd_motion(self, source, event):
        # returns pointer position in display coordinates
        x, y = self.winfo_pointerxy()
        # translate to canvas coordinates
        x = self.canvasx(x)-self.winfo_rootx()
        y = self.canvasy(y)-self.winfo_rooty()
        self.coords(self.dnd_symbol, x, y)
        self.coords(self.dnd_label, x+self.textoff, y)
