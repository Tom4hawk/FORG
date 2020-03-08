# Bookmark.py
# $Id: Bookmark.py,v 1.14 2001/07/11 22:43:09 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# This is a subclass of GopherResource and is used in the Bookmark
# management system of the FORG.
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
from Tkinter import *
from string import *
import xml.etree.ElementTree as ETs

import GopherResource
import List
import ListNode


class Bookmark(GopherResource.GopherResource):
    def __init__(self, res=None):
        GopherResource.GopherResource.__init__(self)

        if res != None:
            # Copy data from the resource to this bookmark.
            self.setName(res.getName())
            self.setHost(res.getHost())
            self.setPort(res.getPort())
            self.setLocator(res.getLocator())
            self.setType(res.getTypeCode())

    def toXML(self):
        """Returns an XML representation of the object."""
        bookmark = ETs.Element("bookmark", href=self.getURL())
        title = ETs.Element("title")
        title.text = self.getName()
        bookmark.append(title)

        return bookmark

    def getURL(self):
        return self.toURL()

    def toData(self):
        return "%s !! gopher://%s:%s/%s" % (self.getName(),
                                            self.getHost(),
                                            self.getPort(),
                                            self.getLocator())
    def __str__(self):
        return self.toString()

    def __repr__(self):
        return self.toString()

    def toString(self):
        if self.getName() != '':
            return "%s: %s" % (self.getHost(), self.getName())
        elif self.getLocator() == '/' or self.getLocator() == '':
            return "%s Root" % self.getHost()
        else:
            return "%s:%s %s" % (self.getHost(), self.getPort(),
                                 self.getLocator())

# Not specific to the bookmark class methods...
def parseBookmark(data):
    data = strip(data)
    items = split(data, "!! ", 2)

    if len(items) < 2:
        print "***Bookmark parse error: Items is: %s" % join(items,"::")
        return None

    bmark = Bookmark()
    try:
        items[1] = strip(items[1])
        bmark.setURL(items[1])
    except Exception, estr:
        print "Returning NONE because I couldn't parse the URL: %s" % estr
        return None

    bmark.setName(items[0])
    return bmark

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

class BookmarkFactory:
    verbose = None

    def __init__(self):
        self.menu        = None
        self.currentMenu = None
        self.currentBmrk = None
        self.folders     = []

    def getMenu(self):
        """Menu object accessor"""
        return self.menu

    def parseResource(self, filename):
        #TODO: catch expat exception
        bookmarksTree = ETs.parse(filename)

        for element in bookmarksTree.getroot():
            self.__parse_element(element)

    def writeXML(self, filename, menu):
        """Writes an XML representation of bookmark menu to file"""
        xbel = ETs.Element("xbel")
        bookmarks = menu.toXML()

        xbel.append(bookmarks)

        tree = ETs.ElementTree(xbel)
        tree.write(filename, "UTF-8")

    def __parse_element(self, item):
        if item.tag == 'folder':
            self.__parse_folder(item)
        elif item.tag == 'bookmark':
            self.__parse_bookmark(item)

    def __parse_folder(self, item):
        # start_folder
        self.currentMenu = BookmarkMenu()
        self.folders.append(self.currentMenu)
        self.lastTag = "folder"
        self.log_verbose("Creating new folder")

        # take care of the folder title
        title = item.find('title')  # folder should have only one title
        self.log_verbose('Setting menu name: ' + title.text)
        self.currentMenu.setName(title.text)

        # it folder so we have to go deep into the rabbit hole
        for element in item:
            self.__parse_element(element)

        # folder processed, let's finish it
        # end_folder
        try:
            finished_folder = self.folders.pop()
        except IndexError:
            self.log_error("****Error parsing XML: </folder> without <folder>")
            return None

        if self.verbose:
            self.log_error("Finishing up folder: %s" % finished_folder.getName())

        if len(self.folders) > 0:
            self.currentMenu = self.folders[len(self.folders) - 1]

            self.log_verbose("Adding submenu \"%s\" to \"%s\"" % (finished_folder.getName(), self.currentMenu.getName()))

            self.currentMenu.addSubmenu(finished_folder)
        else:
            # The stack is empty - assign the main menu to be this item
            # here.
            self.log_verbose("Finished toplevel folder.")
            self.menu = finished_folder

    def __parse_bookmark(self, item):
        # start_bookmark
        self.currentBmrk = Bookmark()
        self.lastTag = "bookmark"

        self.log_verbose("Setting URL to be " + item.attrib['href'])

        try:
            self.currentBmrk.setURL(item.attrib['href'])
        except KeyError:
            self.log_error("**** Error parsing XML: bookmark is missing 'href'")
        except Exception, errstr:
            self.log_error("**** Parse error:  Couldn't parse %s: %s" % (item.attrib['href'], errstr))
            self.currentBmrk = None
            return None

        self.log_verbose("Creating new bookmark")

        # Take care of the bookmark title
        title = item.find('title')  # bookmark should have only one title, we can ignore rest of them
        self.log_verbose("Setting bmark name: " + title.text)
        self.currentBmrk.setName(title.text)

        # end_bookmaark
        self.log_verbose("Inserting new bmark")

        if self.currentBmrk:
            self.currentMenu.insert(BookmarkMenuNode(self.currentBmrk))
        else:
            self.log_error("**** Error parsing XML: could not insert invalid bookmark.")

    #TODO: Create separate logger
    def log_verbose(self, message):
        if self.verbose:
            print(message)

    def log_error(self, message):
        print(message)
