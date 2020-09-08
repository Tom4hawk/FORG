# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
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

import Bookmarks.BookmarkMenu
import Tree
import Dialogs
from Bookmarks.BookmarkFactory import BookmarkFactory
import os
import Options

def traversal_function(node):
    if node.__class__ != Tree.Node:
        print("NODE CLASS: %s" % node.__class__)
        return None
    else:
        bm = node.id
    
    if bm.__class__ == Bookmarks.BookmarkMenu.BookmarkMenu:
        menu = Bookmarks.BookmarkMenu.BookmarkMenu()
        menu.setName(bm.getName())

        # Visit each of the children.  Note that this is children as in what
        # is displayed on the screen after the user has edited the bookmarks
        # with the editor.  This is NOT the children that are listed in the
        # actual BookmarkMenu's data structure, since that may be wrong after
        # the user edits.
        for subnode in node.subnodes:
            rval = traversal_function(subnode)

            if not rval:
                print("**** That's weird.  rval ain't.")
                continue

            # The items are one of two things - BookmarkMenu's or
            # BookmarkMenuNode's.  Figure out which, and add it appropriately.
            # Note that you can't insert a submenu, you have to use addSubmenu
            # which is the reason for this conditional.
            if rval.__class__ == Bookmarks.BookmarkMenu.BookmarkMenu:
                print("Adding submenu:  %s" % rval.getName())
                menu.addSubmenu(rval)
            else:
                # print "Adding ITEM: %s" % rval.__class__
                # print "Adding ITEM: %s %s" % (rval.__class__, rval.getName())
                menunode = Bookmarks.BookmarkMenu.BookmarkMenuNode(rval)
                menu.insert(menunode)

        # Return the generated menu to be added
        return menu
    
    else:  # No children...It's a BookmarkMenuNode
        return bm

class BookmarkEditor(Toplevel):
    def __init__(self, bmtree, ondestroy=None):
        Toplevel.__init__(self)
        self.title("Edit Bookmarks...")
        # Callback to be fired off when this widget is destroyed.
        self.ondestroy = ondestroy
        
        # If user tries to close the window, call self.destroy
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.make_menus()
        self.config(menu=self.menu)
        self.mainBox = Frame(self)
        self.mainBox.pack(fill='both', expand=1)
        
        self.tree = Tree.Tree(self.mainBox, bmtree,
                              rootlabel="Bookmarks", lineflag=0)
        self.tree.grid(row=0, column=0, sticky='NSEW')

        # Make expandable
        self.mainBox.grid_rowconfigure(0, weight=1)
        self.mainBox.grid_columnconfigure(0, weight=1)

        self.vscrollbar = Scrollbar(self.mainBox, orient=VERTICAL)
        self.vscrollbar.grid(row=0, column=1, sticky='NS')
        self.tree.configure(yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.configure(command=self.tree.yview)

        self.hscrollbar = Scrollbar(self.mainBox, orient=HORIZONTAL)
        self.hscrollbar.grid(row=1, column=0, sticky='EW')
        self.tree.configure(xscrollcommand=self.hscrollbar.set)
        self.hscrollbar.configure(command=self.tree.xview)
        
        # must get focus so keys work for demo
        self.tree.focus_set()

        # This is CRITICAL.  Make sure this is done for several reasons:  first
        # it expands the tree so the user can see the whole thing when the
        # editor pops open.  Second, unless items in the tree are expanded,
        # their data elements aren't associated with the tree branches, so in
        # order for the bookmarks to save properly, everything must have been
        # expanded at one point or another, and this just ensures that.
        self.tree.expandAll()
        
        return None

    def destroy(self, *args):
        """User closed the window.  Prompt for saving the bookmarks to
        disk."""

        print("BookmarkEditor::destroy()")
        
        def cb(buttonName, self=self):
            print("Confirm callback: ", buttonName)

            if buttonName == 'OK':
                self.save()

            if self.ondestroy:
                # Call the destroy callback specified by our parent if it's
                # present.
                self.ondestroy()

            # Call superclass method to actually destroy the window.
            Toplevel.destroy(self)
            return None

        # Create a confirmation dialog box
        self._confirmDialog = Pmw.MessageDialog(self,
                                                message_text="Save Bookmarks?",
                                                buttons=('OK', 'Cancel'),
                                                defaultbutton='OK',
                                                title='Save Bookmarks?',
                                                command=cb)
        return None
    
    def getActive(self):
        i = self.tree.getActive()
        print("Active is %s class %s" % (i, i.__class__)) 

    def make_menus(self, *args):
        self.menu = Menu(self)
        self.filemenu = Menu(self.menu)
        self.filemenu.add_command(label="Save",
                                  command=self.save)
        self.filemenu.add_command(label="Create Folder",
                                  command=self.createFolder)
        self.filemenu.add_command(label="Delete Folder",
                                  command=self.deleteFolder)
        self.filemenu.add_command(label="Add a Bookmark",
                                  command=self.addBookmark)
        self.filemenu.add_command(label="Close", command=self.destroy)

        self.editmenu = Menu(self.menu)
        self.editmenu.add_command(label="Cut", command=self.cut)
        self.editmenu.add_command(label="Copy", command=self.copy)
        self.editmenu.add_command(label="Paste", command=self.paste)
        self.editmenu.add_command(label="Delete", command=self.delete)

        self.testmenu = Menu(self.menu)
        self.testmenu.add_command(label="Get Active", command=self.getActive)

        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)
        self.menu.add_cascade(label="Test", menu=self.testmenu)
        return None

    def save(self, *args):
        # data_tree is a Node object, not a BookmarkMenu
        self.tree.expandAll()   # Expand all nodes so data is present in ADT's
        data_tree = self.tree.getTree()
        
        # Take the id attribute out of each Node and string them together.
        # things may have been moved around, so the links inside the data
        # structures are no good, only copy.

        bmarks = traversal_function(data_tree)
        prefs_dir = Options.program_options.getOption('prefs_directory')
        filename = prefs_dir + os.sep + "bookmarks"
        factory = BookmarkFactory()
        
        try:
            factory.writeXML(filename, bmarks)
        except IOError as errstr:
            e = "Could not save bookmarks to\n%s:\n%s" % (filename, errstr)
            d = Dialogs.ErrorDialog(self, e, "Error Saving Bookmarks")

    def insertBookmark(self, bookmark):
        original_cut_buffer = self.tree.getCutBuffer()
        p = self.tree.getActive().parent

        newbm = Tree.Node(parent=None,
                          name=bookmark.getName(),
                          id=bookmark,
                          closed_icon=Tree.Icons.FILE_ICON,
                          open_icon=None,
                          x=10,
                          y=10,
                          parentwidget=self.tree)

        co = Tree.Cut_Object(newbm, newbm.full_id(), None)

        # Set the cutbuffer to be the custom folder we just created.
        self.tree.setCutBuffer(co)
        # Paste it into the heirarchy
        self.tree.paste()
        # Set the cut buffer back to its original position.
        self.tree.setCutBuffer(original_cut_buffer)
        return None
    
    def addBookmark(self):
        # Prompt the user for info.  After the info is completed,
        # insertBookmark will be called with a GopherResponse object as an
        # argument.
        dialog = Dialogs.NewBookmarkDialog(parentwin=self,
                                           cmd=self.insertBookmark)
        return None
    
    def createFolder(self, folderName=None):
        # Basically, just create a Cut_Object, and then call the paste method
        # to insert it into the tree.  Make sure to preserve the cut object
        # that the tree is working with.

        if not folderName:
            self.__newFolderDialog = Dialogs.NewFolderDialog(self,
                                                             self.createFolder)
            return None
        
        original_cut_buffer = self.tree.getCutBuffer()
        bmarkmenu = Bookmarks.BookmarkMenu.BookmarkMenu()
        bmarkmenu.setName(folderName)

        # We have to create a Node to insert into the tree, just like all other
        # nodes in the tree.  Since we're pasting it into the heirarchy and
        # the parent is going to change, we don't need to specify one.  'id'
        # is the data associated with the Node object.
        folder_node = Tree.Node(parent=None,
                                name=folderName,
                                id=bmarkmenu,
                                closed_icon=Tree.Icons.SHUT_ICON,
                                open_icon=Tree.Icons.OPEN_ICON,
                                x=10,
                                y=10,
                                parentwidget=self.tree)

        # Create a Cut_Object.  This is done just as it is done in the
        # Node.cut() method in Tree.py - we have to use our custom created
        # node in order to create this Cut_Object.
        co = Tree.Cut_Object(folder_node, folder_node.full_id(), 1)

        # Set the cutbuffer to be the custom folder we just created.
        self.tree.setCutBuffer(co)
        
        # Paste it into the heirarchy
        self.tree.paste()
        
        # Set the cut buffer back to its original position.
        self.tree.setCutBuffer(original_cut_buffer)
        return None

    
    def deleteFolder(self, *args):
        if not self.tree.getActive().isFolder():
            errstr = "Error:\nThe selected item\nisn't a folder."
            err = Dialogs.ErrorDialog(self, errstr, "Error")
        else:
            cutBuffer = self.tree.getCutBuffer()
            # Delete the item using the cut operation
            self.tree.cut()

            # Restore the old cutbuffer.  Normally after deleting whatever we
            # deleted would be in the cut buffer, but since we're deleting and
            # not cutting, it need not be in the cutbuffer.
            self.tree.setCutBuffer(cutBuffer)
        return None

    def delete(self, *args):
        """Deletes the currently selected node out of the tree."""
        a = self.tree.getActive()

        if a == self.tree.getRoot():
            d = Dialogs.ErrorDialog(self,
                                    "Error:\nYou cannot delete the root.")
            return None

        # Get the old cut buffer
        cutbuf = self.tree.getCutBuffer()
        # Cut the item out (which overwrites the cutbuffer)
        self.cut()
        # Set the old cutbuffer back, meaning that the deleted item is gone
        # forever.
        self.tree.setCutBuffer(cutbuf)
        return None

    def cut(self, *args):
        """Cuts the selected node out of the tree."""
        a = self.tree.getActive()

        if a == self.tree.getRoot():
            # Bad mojo.  You can't cut the root node.
            d = Dialogs.ErrorDialog(self,
                                    "Error:\nYou cannot cut the root element")
            return None
        
        return self.tree.cut()
    
    def copy(self, *args):
        a = self.tree.getActive()

        if a == self.tree.getRoot():
            # Nope, can't copy the root.
            # Should we allow this?  They couldn't paste it in at the same
            # level, but they could paste it in at a sublevel.  I don't
            # know why anybody would want to have a subfolder, but they
            # might.  So let's flag this with a FIXME with the implementation
            # note that if you're going to allow this you can't use the
            # cut() method to do it.
            d = Dialogs.ErrorDialog(self,
                                    "Error:\nYou cannot copy the root element")
            return None
        
        self.cut()
        return self.paste()
    def paste(self, *args):
        if self.tree.getCutBuffer():
            return self.tree.paste()
        else:
            d = Dialogs.ErrorDialog(self,
                                    "There is no active\nbookmark to paste")





