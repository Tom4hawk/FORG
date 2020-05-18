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

from Tkinter import Menu
from string import strip
from xml.etree import ElementTree as ETs

import List
import ListNode
from Bookmarks.Bookmark import Bookmark


# Subclass ListNode just for naming purposes so BookmarkMenuNodes can be
# dealt with inside of BookmarkMenus
class BookmarkMenuNode(ListNode.ListNode):
    pass


# BookmarkMenu is to organize heirarchical menus of bookmarks which will be
# editable by the user.
class BookmarkMenu(List.List):
    verbose = None
    def __init__(self, menuName=" "):
        List.List.__init__(self)
        self.menuName = menuName
        return None
    def getName(self):
        if strip(self.menuName) > 0:
            return self.menuName
        else:
            self.setName("Bookmarks")
            return self.menuName
        return "Error fetching name"

    def setName(self, newname):
        self.menuName = newname
        return self.menuName

    def toString(self):
        return "BookmarkMenu: \"%s\"" % self.getName()

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def insert(self, item, truncate=0):
        """Overrides the insert method to always pass a truncate argument of
        0 so the list is never truncated on insertions."""
        return List.List.insert(self, item, 0)

    def addSubmenu(self, menu):
        """Adds menu as a submenu of this menu"""
        if menu.__class__ != BookmarkMenu and menu.__class__ != Bookmark:
            raise Exception, "Cannot add a non-Bookmark/Menu as submenu"
        return self.insert(BookmarkMenuNode(menu))



    def toXML(self):
        """Returns an XML representation of this object.  This is called
        recursively"""

        if self.verbose:
            print "BookmarkMenu.toXML()"

        folder = ETs.Element("folder")
        title = ETs.Element("title")
        title.text = self.getName()
        folder.append(title)

        def fn(item, parent=folder):
            data = item.getData()
            # It doesn't matter which kind it is, whether it's a
            # Bookmark or a BookmarkMenu since they both have toXML() methods
            # and they'll take it from here.  If it's a BookmarkMenu, this
            # will happen recursively.
            node = data.toXML()
            parent.append(node)

            return data.getName()

        # Apply the above function to each item in the menu
        self.traverse(fn)

        return folder

    def getTkMenu(self, parent_widget, callback):
        """Return a Tk Menu object which is suitable for being added to other
        submenus.  parent_widget is the menu you will add it to, and callback
        is a function that takes exactly one argument.  That argument is the
        Bookmark object that the user-clicked item represents."""
        # This is the menu we will return.
        m = Menu(parent_widget)

        # Create a subfunction to deal with each item in the list.
        # This way since this object already extends List and we already have
        # a traverse function, we can go through the entire list in order
        def fn(listitem, cb=callback, addTo=m):
            # Each item in the list is a ListNode, not a Bookmark, so get the
            # data out of the ListNode.
            data = listitem.getData()

            def real_callback(item=data, oldCallback=cb):
                """This is a way of converting a callback that takes no
                arguments into one that takes two for our purposes.  The
                user passes in a callback function that takes only one
                parameter (the resource you want to go to) and this is
                the actual function that is bound to the action, which calls
                the user defined function with the appropriate argument"""
                return oldCallback(item)

            try:
                # If it's a menu, then add the submenu recursively.
                if data.__class__ == BookmarkMenu:
                    addTo.add_cascade(label=data.getName(),
                                      menu=data.getTkMenu(addTo, cb))
                else:
                    # Otherwise add a regular command into the menu.
                    addTo.add_command(label=data.getName(),
                                      command=real_callback)
            except:
                pass
            return data.getName()

        # Apply the above to each item in the list, adding menu items and
        # submenus where needed.
        self.traverse(fn)   # Don't care about the return results.

        return m
