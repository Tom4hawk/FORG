# TkGui.py
# $Id: TkGui.py,v 1.56 2001/07/14 23:50:49 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
#
# This handles the GUI of the program, displaying, bookmarks, etc.
# This module is usually called by the starter script.  All other modules
# are usually invoked through this one as the GUI needs them.
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
# Python-wide modules not specific to this program
import os

# TODO: Only here to prevent error "partially initialized module 'GopherResponse'"
# (most likely due to a circular import)
import AskForm

# Data structures, connections, and the like.
import utils
import Options
import GopherResource
import Associations

from Bookmarks.BookmarkEditor import BookmarkEditor
from Bookmarks.Bookmark import Bookmark
from Bookmarks.BookmarkMenu import BookmarkMenu, BookmarkMenuNode
from Bookmarks.BookmarkFactory import BookmarkFactory
from xml.etree.ElementTree import ParseError


# GUI specific modules.
from tkinter import *
import AssociationsEditor         # GUI editor for association rules
import forgtk                       # The guts of the entire application
import Pmw                        # Python Mega Widgets
import Dialogs                    # FORG specific dialogs



class TkGui(Tk):
    verbose = None
    MENU_FILE       = 1
    MENU_EDIT       = 2
    MENU_NAVIGATION = 3
    MENU_BOOKMARKS  = 4
    MENU_OPTIONS    = 5
    MENU_HELP       = 6

    RED             = '#FF0000'
    GREEN           = '#00FF00'
    BLUE            = '#0000FF'
    
    def __init__(self, URL=None):
        """Create an instance of the gopher program."""
        Tk.__init__(self)

        self.bookmarks = None

        self.loadOptions()              # Load program options from disk
        self.loadBookmarks()            # Load program bookmarks from disk
        self.createAssociations()       # Load program associations

        self.options_filename = self.getPrefsDirectory() + os.sep + "options"

        # Load options into the root window and all subwindows.
        try:
            if utils.file_exists(self.options_filename):
                self.option_readfile(self.options_filename)
        except Exception as errstr:
            print(("***Error loading options from %s: %s" %
                  (self.options_filename, errstr)))

        if self.verbose:
            print("OPTIONS:\n%s" % Options.program_options.toString())

        self.minsize(550, 550)
        self.title("FORG v. %s" % forgtk.getVersion())

        self.saveFileDialog        = None
        self.DOWNLOAD_ME           = None     # Thread control variable
        self.CURRENTLY_DOWNLOADING = None     # Are we downloading right now?
        self.LAUNCH_ME             = None     # Thread control variable
        self.WIDGET_ENTRY          = 0

        self.mainBox = Frame(self)
        self.mainBox.pack(fill='both', expand=1)
        self.make_menus()
        self.config(menu=self.menu)
        self.buttonBar = Frame(self.mainBox)
        self.navBox    = Frame(self.mainBox)
        self.buttonBar.pack(fill='x', expand=0)
        self.navBox.pack(fill='x', expand=0)

        self.BACKWARD = Button(self.buttonBar, text='Back', command=self.goBackward)
        self.FORWARD  = Button(self.buttonBar, text='Forward', command=self.goForward)
        # self.STOP   = Button(self.buttonBar, text='Stop',
        #                      command=self.stop)
        self.RELOAD   = Button(self.buttonBar, text='Reload', command=self.reload)
        self.HOME     = Button(self.buttonBar, text='Home', command=self.goHome)

        self.BACKWARD.pack(side='left')
        self.FORWARD.pack(side='left')
        # self.STOP.pack(side='left')
        self.RELOAD.pack(side='left')
        self.HOME.pack(side='left')

        if Options.program_options.getOption('use_url_format'):
            self.urlLabel = Label(self.navBox, text="Location:")
            self.urlEntry = Entry(self.navBox)
            self.urlEntry.bind("<Return>", self.go)

            self.urlLabel.pack(side='left')
            self.urlEntry.pack(side='left', expand=1, fill='x')
        else:
            self.hostLabel = Label(self.navBox, text='Host:')
            self.hostEntry = Entry(self.navBox)
            self.resourceLabel = Label(self.navBox, text='Resource:')
            self.resourceEntry = Entry(self.navBox, text="/")
            self.resourceEntry.insert('end', '/')
            self.portLabel = Label(self.navBox, text='Port:')
            self.portEntry = Entry(self.navBox, width=5)

            self.portEntry.insert('end', '70')
            self.hostLabel.grid(row=0, column=0, sticky=W)
            self.hostEntry.grid(row=0, column=1, columnspan=2, sticky=W)
            self.resourceLabel.grid(row=0, column=3, sticky=W)
            self.resourceEntry.grid(row=0, column=4, columnspan=2, sticky=W)
            self.portLabel.grid(row=0, column=6, sticky=W)
            self.portEntry.grid(row=0, column=7, sticky=W) # No colspan: short box

        self.gobutton = Button(self.navBox, text='Go', command=self.go)

        if Options.program_options.getOption('use_url_format'):
            self.gobutton.pack(side='right')
        else:
            self.gobutton.grid(row=0, column=8, sticky=W)

        resource = GopherResource.GopherResource()

        if URL is not None:
            resource.setURL(URL)
        else:
            resource.setURL(Options.program_options.getOption('home'))

        self.CONTENT_BOX = forgtk.ForgTk(parent_widget=self.mainBox,
                                         parent_object=self,
                                         resource=resource)

        self.messageBar = Pmw.MessageBar(self.mainBox,
                                         entry_width = 80,
                                         entry_relief='groove',
                                         labelpos = 'w',
                                         label_text = 'Status:')

        self.CONTENT_BOX.setMessageBar(self.messageBar)

        self.CONTENT_BOX.pack(expand=1, fill='both')
        self.messageBar.pack(expand=0, fill='x')
        utils.msg(self.messageBar, "Ready")

        # Call fn when the window is destroyed.
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.setLocation(self.CONTENT_BOX.getResource())
        return None

    def getCache(self):
        return Options.program_options.cache

    def stats(self, *args):
        return self.CONTENT_BOX.stats()

    def destroy(self, *args):
        """Overridden destroy method for the application.  This does
        cleanup, particularly with the various living threads before
        destroying the GUI on screen"""
        
        self.DOWNLOAD_ME = "DIE"    # Kill the two other threads with this
        self.LAUNCH_ME   = "DIE"    # 'message' to them.
                                    # They will see this.

        # Things that need to be done before we exit...

        if Options.program_options.getOption('save_options_on_exit'):
            # self.messageBar.message('state', "Saving program options...")
            print("Saving options on exit...")
            self.saveOptions()

        if Options.program_options.getOption('delete_cache_on_exit'):
            print("Deleting cache on exit...")
            Options.program_options.cache.deleteCacheNoPrompt()
        
        Tk.destroy(self)
        print("MT:  Exit")

    def editAssociations(self, *args):
        """Callback: opens the associations editor and lets the users change
        which programs launch on which filetypes."""
        x = AssociationsEditor.AssociationsEditor(
            self, Options.program_options.associations
            )
        return None

    def notYetImplemented(self, *args):
        """Opens a dialog for the user to see that the feature hasn't been
        implemented yet."""
        self.genericMessage(
            "Contribute to the Programmer Pizza Fund today!\n" +
            "Maybe that will help get this feature put into\n" +
            "the program!")
        return None
    
    def setAssociations(self, assocList):
        """Modifier: associates a list of associations usually from the
        AssociationsEditor to this object."""
        Options.program_options.setAssociations(assocList)
        return None
    
    def createAssociations(self, *args):
        """Creates a set of default associations.  These are mostly UNIX
        centric unless I change them and forget to update this docstring.  :)
        """
        Options.program_options.setAssociations(Associations.Associations())

        filename = self.getPrefsDirectory() + os.sep + "forg-associations"
        self.loadAssociations(filename)

        if Options.program_options.getAssociations().isEmpty():
            print("ADDING DEFAULT ASSOCIATIONS")
            # Add defaults if there isn't anything in the association list.
            images = [".gif", ".jpg", ".bmp", ".xpm", ".xbm", ".png", ".jpeg", ".tif", ".tiff"]

            for item in images:
                Options.program_options.associations.addAssociation(item, "eeyes $1")

            browser_stuff = [".html", ".htm", ".css"]
            for item in browser_stuff:
                cmd = "netscape $1"
                Options.program_options.associations.addAssociation(item, cmd)

            Options.program_options.associations.addAssociation(".pdf", "xpdf $1")
            Options.program_options.associations.addAssociation(".ps", "gv $1")
        return None

    def genericMessage(self, str, title='Information:'):
        """Given a string, pops up a dialog with the appropriate title and
        content string."""
        x = Dialogs.InformationDialog(self, str, title)
        return None
        
    def genericError(self, errstr, title='Error:'):
        """Given an error string, pops up a dialog with the same title and
        text, alerting the user to something or other."""
        x = Dialogs.ErrorDialog(self, errstr, title)
        return None

    def find(self, *args):
        """Wrapper function for find.  When the find feature is used, this
        gets called to call the find feature in the child widget."""
        
        wid = self.CONTENT_BOX.navList.getCurrent().getData().getWidget()
        self._find_dialog = Dialogs.FindDialog(self, wid, self)
        return None

    def addBookmark(self, *args):
        """Callback: take the current content frame and add the resource
        associated to it to the bookmark list.  The new bookmark is appended
        at the end of the bookmarks menu"""

        resource = self.CONTENT_BOX.getResource()
        foo = Bookmark(resource)

        # Save the bookmark...
        self.bookmarks.insert(BookmarkMenuNode(foo))
        self.saveBookmarks()

        self.reloadBookmarks()
        return None

    def reloadBookmarks(self, *args):
        """Reloads bookmarks from disk, and replaces the current Bookmark
        menu with the new one loaded from disk."""
        
        print("*** Reloading bookmarks from disk after edit.")
        self.loadBookmarks()

        # self.bookmarks now holds the freshly edited copy of the bookmarks.
        # Create a new Tk menu based off of them.

        # Destroy the old menu and insert the new.
        self.bookmarkTkMenu = self.buildTkBookmarksMenu(self.menu, self.bookmarks)

        self.menu.delete(self.MENU_BOOKMARKS)
        self.menu.insert_cascade(index=self.MENU_BOOKMARKS,
                                 label=self.bookmarks.getName(),
                                 menu=self.bookmarkTkMenu)
        return None

    def getPrefsDirectory(self):
        return Options.program_options.getOption('prefs_directory')

    def loadAssociations(self, filename=None):
        if filename is None:
            filename = self.getPrefsDirectory() + os.sep + "forg-associations"

        try:
            Options.program_options.associations.loadFromFile(filename)
        except IOError as errstr:
            print("****Cannot load associations from %s: %s" % (filename, str))
            return 0 # Failure
        return 1  # Success

    def loadOptions(self, filename=None):
        if filename is None:
            filename = self.getPrefsDirectory() + os.sep + "forgrc"

        try:
            Options.program_options.parseFile(filename)
        except IOError as errstr:
            print("**** Couldn't parse options at %s: %s" % (filename, errstr))
            return None
        
        print("****Successfully loaded options from disk.")
        return 1
    
    def saveOptions(self, *args):
        """Saves the user options to a file in their home directory.  Who knows
        what happens on windows boxen."""

        filename = self.getPrefsDirectory() + os.sep + "forg-associations"

        try:
            Options.program_options.associations.writeToFile(filename)
        except IOError as str:
            print("***Error saving associations to disk: %s" % str)

        ofilename = self.getPrefsDirectory() + os.sep + "forgrc"
        
        try:
            Options.program_options.save()
        except IOError as str:
            self.genericError("Couldn't write options to file:\n%s" % str)

        utils.msg(self.messageBar, "Finished saving options.")
        return None

    def loadBookmarks(self, *args):
        self.bookmarks = BookmarkMenu("Bookmarks")
        filename = self.getPrefsDirectory() + os.sep + "bookmarks"
        
        try:
            factory = BookmarkFactory()
            factory.parseResource(filename)
            self.bookmarks = factory.getMenu()
        except (IOError, ParseError) as errstr:
            print("****Couldn't load bookmarks at %s: %s" % (filename, errstr))
            return None
        
        print("****Bookmarks successfully loaded from disk.")
        return 1
    
    def saveBookmarks(self, *args):
        filename = self.getPrefsDirectory() + os.sep + "bookmarks"

        try:
            factory = BookmarkFactory()
            factory.writeXML(filename, self.bookmarks)
        except IOError as errstr:
            print("****Couldn't save bookmarks to %s: %s" % (filename, errstr))
            return None
        print("****Bookmarks successfully saved to %s" % filename)
        return 1

    def stop(self, *args):
        """Just set green light to a false value, and wait for the download
        thread to get the point.  It will quit once it sees this."""
        return Options.program_options.redLight()

    def goForward(self, *args):
        self.CONTENT_BOX.goForward()
        self.setLocation(self.CONTENT_BOX.getResource())
    
    def goBackward(self, *args):
        self.CONTENT_BOX.goBackward()
        self.setLocation(self.CONTENT_BOX.getResource())
    
    def go(self, *rest):
        """This is what happens when the 'Go' button is clicked.  Information
        about the host, port, locator is fetched from the entry boxes, and
        the program goes there.  (Or tries, anyway)"""

        if Options.program_options.getOption('use_url_format'):
            url = self.urlEntry.get().strip()

            ind = url.find("://")
            if ind != -1:
                proto = url[0:ind]
                if proto.lower() != "gopher":
                    self.genericError("Protocol\n\"%s\"\nnot supported." % proto)
                    return None
            elif url[0:9].lower() != "gopher://":
                url = "gopher://" + url
                    
            res = GopherResource.GopherResource()
            try:
                res.setURL(url)
            except Exception as estr:
                self.genericError("Invalid gopher URL:\n%s\n%s" % url, estr)
                return None
        else:
            host    = self.hostEntry.get()
            port    = self.portEntry.get()
            locator = self.resourceEntry.get()
            
            if locator == '':
                locator = "/"

            if port == '' or port < 0:
                port = 70
        
            res  = GopherResource.GopherResource('1', host, port, locator, "%s Root" % host)

        # Either way, go there.
        self.goElsewhere(res)

    def goElsewhere(self, resource, usecache=1, *args):
        self.CONTENT_BOX.goElsewhere(resource, usecache, args)
        self.setLocation(self.CONTENT_BOX.getResource())

    def openURL(self, URL):
        resource = GopherResource.GopherResource()
        resource.setURL(URL)
        return self.goElsewhere(resource)
        
    def showOpenURL(self, *args):
        d = Dialogs.OpenURLDialog(self, self.openURL)
        return None

    def saveFile(self, *args):
        return self.CONTENT_BOX.saveFile()

    def popupMenu(self, event):
        """Display pop-up menu on right click on a message"""
        self.popup.tk_popup(event.x_root, event.y_root)
        
    def createPopup(self):
        """Pop-up menu on right click on a message"""
        self.popup = Menu(self)
        self.popup['tearoff'] = FALSE
        self.popup.add_command(label='Save', command=self.CONTENT_BOX.saveFile)
        self.popup.add_command(label='Back', command=self.CONTENT_BOX.goBackward)
        self.popup.add_command(label='Forward', command=self.CONTENT_BOX.goForward)

    def change_content_hook(self, resource):
        """This function is called by the child FORG instance whenever
        content is changed.  The resource argument is the GopherResource
        object corresponding to the content currently in the window."""
        return self.setLocation(resource)

    def setLocation(self, resource):
        """Takes a resource, and sets the location information at the top
        of the screen to the information in the resource.  If you're going to
        a certain location, this gets called to update what the user sees as
        the location."""

        if Options.program_options.getOption('use_url_format'):
            URL = resource.toURL()

            # Translate spaces.  This is ONLY done because this is the way
            # other programs like to get their URLs, not because it needs to
            # be this way per se.  Users copy and paste out of this location
            # bar, so put a standard style URL there.
            URL = re.sub(" ", "%20", URL)
            self.urlEntry.delete(0, 'end')
            self.urlEntry.insert('end', URL)
        else:
            self.hostEntry.delete(0, 'end')
            self.resourceEntry.delete(0, 'end')
            self.portEntry.delete(0, 'end')

            self.hostEntry.insert('end', resource.getHost())
            self.resourceEntry.insert('end', resource.getLocator())
            self.portEntry.insert('end', resource.getPort())

        return None

    def dumpQueue(self, *rest):
        return self.CONTENT_BOX.dumpQueue()

    def reload(self, *rest):
        return self.CONTENT_BOX.reload()

    def about(self):

        window = Toplevel()

        # This prevents about window from being resizeable. Most Linux WMs will also hide maximize button
        window.resizable(0, 0)

        window.title("About FORG")

        forg_version = Label(window, text="Version " + forgtk.getVersion())
        forg_copyright = Label(window, text="Copyright 2000, 2001 David Allen <mda@idatar.com> \n" +
                                               "Copyright 2019-2021 Tom4hawk")
        forg_license = Label(window, text="This program is licensed under the GNU General Public License\n" +
                                             "For more information, please see\n" +
                                             "https://www.gnu.org/")

        close_button = Button(window, text="Close", command=window.destroy)

        forg_version.pack(padx=50, pady=5)
        forg_copyright.pack(padx=50, pady=5)
        forg_license.pack(padx=50, pady=5)

        close_button.pack(fill='x', padx=50, pady=5)

    def quit(self, *args):
        """Quit the entire program.  Caller may have something after this."""
        self.destroy()

    def editBookmarks(self, *args):
        ed = BookmarkEditor(self.bookmarks, ondestroy=self.reloadBookmarks)

    def buildTkBookmarksMenu(self, parent_menu, bookmarks):
        def fn(item, self=self):
            return self.goElsewhere(item)
        
        newTkMenu = bookmarks.getTkMenu(parent_menu, fn)
        newTkMenu.insert_separator(index=1)
        newTkMenu.insert_command(index=0, label="Edit Bookmarks", command=self.editBookmarks)
        newTkMenu.insert_command(index=1, label="Bookmark this page", command=self.addBookmark)
        return newTkMenu

    def goHome(self, *args):
        """Redirects the content of the main window to the user's chosen
        home site."""
        
        url = Options.program_options.getOption('home')

        if url:
            res = GopherResource.GopherResource()
            res.setURL(url)
            return self.goElsewhere(res)
        else:
            d = Dialogs.ErrorDialog(self,
                                    "You don't have a home site specified",
                                    "Error:  Cannot locate home site")
            return None
        
    def setHome(self, *args):
        url = self.CONTENT_BOX.getResource().toURL()
        Options.program_options.setOption('home', url)
        return None
    
    def make_menus(self):
        """Create the menuing system"""
        self.menu = Menu(self.mainBox)
        self.filemenu = Menu(self.menu)
        self.filemenu.add_command(label='Open URL', command=self.showOpenURL)
        self.filemenu.add_command(label='Save', command=self.saveFile)
        self.filemenu.add_command(label='Quit', underline=0, command=self.quit)

        self.editmenu = Menu(self.menu)
        self.editmenu.add_command(label="Find", command=self.find)

        self.navmenu = Menu(self.menu)
        self.navmenu.add_command(label="Forward", command=self.goForward)
        self.navmenu.add_command(label="Backward", command=self.goBackward)
        self.navmenu.add_command(label="Reload", command=self.reload)

        self.optionsmenu = Menu(self.menu)
        self.optionsmenu.add_command(label='Associations', command=self.editAssociations)
        self.optionsmenu.add_command(label="Save Options/Associations", command=self.saveOptions)
        self.optionsmenu.add_command(label="Reload Options/Associations", command=self.loadOptions)
        self.optionsmenu.add_command(label="Set This Site as My Home", command=self.setHome)

        def purgeCacheWrapper(c=Options.program_options.cache, parent=self):
            c.emptyCache(parent)
            
        self.omenucache = Menu(self.optionsmenu)
        self.omenucache.add_command(label="Purge Cache",  command=purgeCacheWrapper)
        self.omenucache.add_command(label="Cache Statistics", command=self.stats)
        
        self.optionsmenu.add_cascade(label="Cache", menu=self.omenucache)
        
        # Default value of 'show_cached'
        scstatus   = Options.program_options.getOption('show_cached')
        # Function to toggle the value of 'show_cached'
        sccallback = Options.program_options.makeToggleWrapper('show_cached')

        # key          = 'grab_resource_info'
        # gristatus    = Options.program_options.getOption(key)
        # gricallback  = Options.program_options.makeToggleWrapper(key)

        key          = "delete_cache_on_exit"
        dcstatus     = Options.program_options.getOption(key)
        dccallback   = Options.program_options.makeToggleWrapper(key)

        key          = "use_PIL"
        upstatus     = Options.program_options.getOption(key)
        upcallback   = Options.program_options.makeToggleWrapper(key)

        key          = "save_options_on_exit"
        sooestatus   = Options.program_options.getOption(key)
        sooecallback = Options.program_options.makeToggleWrapper(key)

        key          = "strip_carraige_returns"
        scrstatus    = Options.program_options.getOption(key)
        scrcallback  = Options.program_options.makeToggleWrapper(key)

        key          = "use_cache"
        ucstatus     = Options.program_options.getOption(key)
        uccallback   = Options.program_options.makeToggleWrapper(key)

        # This is a dictionary to hold the IntVar data that gets used to set
        # the default value of the checkbuttons.  Because of some weirdness,
        # if the data isn't held, then it does'nt work properly.  (I.e. if you
        # use a variable only within this following loop to create an IntVar
        # and don't store it outside of the temporary loop, it won't work)
        # So in other words this is data getting put into a quick dictionary
        # "Just Because" and isn't actually going to be used.
        # If you want to see what I'm talking about, try replacing
        # self.followvars with just 'var' as a temporary variable, and it
        # won't work.
        self.followvars = {}
        
        for item in [["Show Cached Status", scstatus, sccallback],
                     ["Save Options On Exit", sooestatus, sooecallback],
                     ["Strip Carriage Returns", scrstatus, scrcallback],
                     ["Use Cache", ucstatus, uccallback],
                     ["Delete Cache on Exit", dcstatus, dccallback],
                     ["Use PIL if Available", upstatus, upcallback]]:
            # Store this variable because python is weird.
            self.followvars[item[0]] = IntVar()

            if item[1]:  self.followvars[item[0]].set(1)
            else:        self.followvars[item[0]].set(0)
            
            self.optionsmenu.add_checkbutton(label=item[0],
                                             indicatoron=TRUE,
                                             # Use the stored varable here...
                                             # bind it to the menu
                                             variable=self.followvars[item[0]],
                                             command=item[2])

        try:
            if self.bookmarkTkMenu:
                self.bookmarkTkMenu = None
        except:
            pass
        
        self.bookmarkTkMenu = self.buildTkBookmarksMenu(self.menu,
                                                        self.bookmarks)
        
        self.helpmenu = Menu(self.menu)
        self.helpmenu.add_command(label='About', command=self.about)

        self.hdebug = Menu(self.helpmenu)
        
        def printopts(opts=Options.program_options):
            print(opts)
            
        self.hdebug.add_command(label="Dump Options", command=printopts)
        self.hdebug.add_command(label="Dump Queue", command=self.dumpQueue)
        self.helpmenu.add_cascade(label='Debug', menu=self.hdebug)        

        for menu_node in [self.filemenu, self.editmenu, self.navmenu,
                          self.bookmarkTkMenu, self.optionsmenu,
                          self.helpmenu]:
            # Disable menu tearoffs.
            menu_node['tearoff'] = FALSE

        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.menu.add_cascade(label="Edit", menu=self.editmenu)
        self.menu.add_cascade(label="Navigation", menu=self.navmenu)
        self.menu.add_cascade(label="Bookmarks", menu=self.bookmarkTkMenu)
        self.menu.add_cascade(label="Options", menu=self.optionsmenu)
        self.menu.add_cascade(label="Help", menu=self.helpmenu)
# END TkGui class

