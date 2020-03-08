import xml.etree.ElementTree as ETs

from Bookmark import Bookmark
from Bookmarks.BookmarkMenu import BookmarkMenuNode, BookmarkMenu


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
        #TODO: Catch expat exception
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
