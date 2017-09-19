#!/usr/bin/python
# GopherGUI.py
# Written by David Allen <s2mdalle@titan.vcu.edu>
# Released under the terms of the GNU General Public License
#
# This module does most of the graphical interface work related to the program.
# In order to start the main program, import gtk, create a GopherGUI object,
# and call mainloop() in gtk.
###############################################################################

# Python-wide modules.
import os
import string
import regsub

# GUI specific modules.
from gtk            import *
from GDK            import *
from TextFrame import *

# Data structures, connections, and the like.
from GopherConnection import *
from GopherResponse import *
from gopher import *
from List import *
from Associations import *

GLOBAL_WINDOW_COUNT = 0

class GopherGUI:    
    def __init__(self):
        WIDTH  = 600
        HEIGHT = 600

        self.WIDGET_ENTRY   = 0
        self.RESOURCE_ENTRY = 1
        self.RESPONSE_ENTRY = 2

        self.currentIndex   = -1

        # self.navList contains ONLY ListNode() objects
        self.navList = List()
        self.currentContent = None

        self.createAssociations()
        
        self.window = GtkWindow(WINDOW_TOPLEVEL)        
        self.window.set_default_size(width=WIDTH, height=HEIGHT)        
        self.frame  = GtkVBox(0, 0)
        self.topBar = GtkHBox(0, 0)

        self.hostEntry    = GtkEntry()
        self.portEntry    = GtkEntry()
        self.locatorEntry = GtkEntry()

        self.portEntry.set_max_length(6)
        
        self.okHostPort = GtkButton(label="  Go  ")
        self.okHostPort.connect("clicked", self.go)
        self.topBar.pack_start(GtkLabel("Host: "),
                               expand=FALSE, fill=FALSE)
        self.topBar.pack_start(self.hostEntry, expand=TRUE, fill=TRUE)
        self.topBar.pack_start(GtkLabel("Locator: "),
                               expand=FALSE, fill=FALSE)
        self.topBar.pack_start(self.locatorEntry,
                               expand=FALSE, fill=TRUE)
        self.topBar.pack_start(GtkLabel("Port: "),
                               expand=FALSE, fill=FALSE)
        self.topBar.pack_start(self.portEntry, expand=FALSE, fill=FALSE)
        self.topBar.pack_start(self.okHostPort, expand=FALSE, fill=FALSE)

        self.hostEntry.set_text("quux.org")
        self.portEntry.set_text("70")
        
        self.menuBar = GtkMenuBar()
        menus = self.makeMenus()
        for menu in menus:
            self.menuBar.append(menu)
            
        self.handleBox = GtkHandleBox()
        self.handleBox.add(self.menuBar)

        self.notebook = GtkNotebook()
        self.notebook.set_homogeneous_tabs(FALSE)
        
        resource = GopherResource(RESPONSE_DIR,
                                  "/", "quux.org", 70,
                                  "Quux.org root")
        self.CONTENT_BOX = GtkVBox(0,0)

        contentKey = self.createContentFrame(resource)
        self.changeContent(contentKey[0])

        # The data for ListNodes in this list is a three-item list:
        # [widget, resource, response]
        # widget is the actual GTK+ widget that is packed into the screen.
        # resource is the GopherResource object used to identify a connection.
        # response is the GopherRespones object used to cache the output of
        # a qeury with the server.
        self.navList.insert(ListNode(contentKey))

        self.navBar = GtkHBox(0,0)
        forward = GtkButton("Forward")
        back    = GtkButton("Back")
        forward.connect("clicked", self.goForward)
        back.connect("clicked", self.goBackward)
        self.navBar.pack_start(forward, expand=FALSE, fill=FALSE)
        self.navBar.pack_start(back, expand=FALSE, fill=FALSE)
        
        self.frame.pack_start(self.handleBox, expand=FALSE, fill=TRUE)
        self.frame.pack_start(self.topBar, expand=FALSE, fill=TRUE)
        self.frame.pack_start(self.navBar, expand=FALSE, fill=TRUE)
        self.frame.pack_start(self.CONTENT_BOX, expand=TRUE, fill=TRUE)
        self.window.signal_connect('destroy', self.destroy)
        self.window.add(self.frame)

        return None

    def changeContent(self, newwid):
        if self.currentContent != None:
            self.currentContent.destroy()
        self.CONTENT_BOX.pack_start(newwid, expand=TRUE, fill=TRUE)
        self.currentContent = newwid
        return self.currentContent

    def createAssociations(self, *args):
        self.associations = Associations()
        images = [".gif", ".jpg", ".bmp", ".xpm", ".xbm",
                  ".png", ".jpeg", ".tif", ".tiff" ]

        for item in images:
            self.associations.addAssociation(item, "eeyes $1")

        browser_stuff = [".html", ".htm", ".css"]

        for item in browser_stuff:
            self.associations.addAssociation(item, "netscape $1")

    def printItems(self):
        print "Items on stack:"
        for item in self.contentStack:
            print item.toString()

    def xpmToWidget(self, file, parent):
        pixmap = None
        return pixmap

    def go(self, *rest):
        host    = self.hostEntry.get_text()
        port    = self.portEntry.get_text()
        locator = self.locatorEntry.get_text()

        if locator == '':
            locator = "/"
        
        res  = GopherResource('1', locator,
                              host, port, "%s Root" % host)
        self.goElsewhere(None, res)

    def goElsewhere(self, emitter, resource):
        contentKey = self.createContentFrame(resource)
        self.changeContent(contentKey[0])
        self.navList.insert(ListNode(contentKey))
        return None

    def goForward(self, *rest):
        try:
            node = self.navList.getNext()
            wid  = self.responseToWidget(data[self.RESPONSE_ENTRY],
                                         data[self.RESOURCE_ENTRY])
            self.changeContent(wid)
        except ListException, errstr:
            print "Couldn't get next: %s" % errstr
        return None
    
    def goBackward(self, *rest):
        try:
            node = self.navList.getPrev()
            data = node.getData()
            wid  = self.responseToWidget(data[self.RESPONSE_ENTRY],
                                         data[self.RESOURCE_ENTRY])
            self.changeContent(wid)
        except ListException, errstr:
            print "Couldn't get prev: %s" % errstr

    def clone(self, *args):
        x = GopherGUI()
        x.show()
        return None

    def createContentFrame(self, resource):                
        conn = GopherConnection("quux.org", 70)
        resp = conn.getResource(resource)
        wid  = self.responseToWidget(resp, resource)
        return [wid, resource, resp]

    # Takes a response object and turns it into a graphical box.
    def responseToWidget(self, resp, resource):
        labeltext = "%s:%d" % (resource.getHost(), int(resource.getPort()))
        label2 = "\"%s\" ID %s" % (resource.getName(), resource.getLocator())

        scrolled_window = GtkScrolledWindow()
        sbox = GtkVBox(0, 0)
        
        sbox.pack_start(GtkLabel(labeltext),
                        expand=FALSE, fill=FALSE)
        sbox.pack_start(GtkLabel(label2),
                        expand=FALSE, fill=FALSE)
        
        if resp.getData() != None:
            pane = GtkVBox(0, 0)
            print "DATA:"
            print resp.getData()
            textwid = TextFrame(regsub.sub("\r", "", resp.getData()))
            pane.pack_start(textwid, expand=TRUE, fill=TRUE)
            pane.show_all()
            return pane
        else:
            print "RESPONSES:"
            pane          = GtkVBox(0, 0)
            responses     = resp.getResponses()
            table         = GtkTable(rows=len(responses),
                                     cols=2,
                                     homogeneous=FALSE)
            for x in range(0, len(responses)):
                r = responses[x]
                print "Response: %s" % r.getName()
                b = GtkButton(r.getName())
                b.signal_connect("clicked", self.goElsewhere, r)
                b.set_relief(RELIEF_NONE)
                table.attach(GtkLabel(r.getType()),
                             0, 1, x, (x+1),
                             xoptions=0, yoptions=0,
                             ypadding=0, xpadding=0)
                table.attach(b,
                             1, 2, x, (x+1),
                             xoptions=EXPAND|FILL, yoptions=0,
                             ypadding=0, xpadding=0)
                
            pane.pack_start(table, expand=TRUE, fill=TRUE)
            sbox.pack_start(pane, expand=TRUE, fill=TRUE)
            scrolled_window.add_with_viewport(sbox)
            scrolled_window.show_all()
            return scrolled_window
        return None # Never happens
    
    def closeWindow(self, *args):
        self.window.destroy()
        # GLOBAL_WINDOW_COUNT = GLOBAL_WINDOW_COUNT - 1
        # if GLOBAL_WINDOW_COUNT == 0:
        #    mainquit()
    
    def destroy(self, data=None, auxdata=None):
        self.window.destroy()
        mainquit()
        return None
    
    def show(self):
        self.window.set_policy(FALSE, TRUE, TRUE)
        self.window.show_all()
        return None    
    def makeMenus(self):
        fileMenu       = GtkMenuItem(label="File")
        helpMenu       = GtkMenuItem(label="Help")
        navMenu        = GtkMenuItem(label="Navigation")
        fm = GtkMenu()
        nm = GtkMenu()
        hm = GtkMenu()

        file_new_win = GtkMenuItem(label="New Window")
        file_new_win.connect("activate", self.clone)

        file_close_win = GtkMenuItem(label="Close Window")
        file_close_win.connect("activate", self.closeWindow)
        
        file_exit   = GtkMenuItem(label='Exit')
        file_exit.connect('activate', self.destroy)

        nav_forward = GtkMenuItem(label="Forward")
        nav_backward = GtkMenuItem(label="Backward")

        nav_forward.connect("activate", self.goForward)
        nav_backward.connect("activate", self.goBackward)
        
        help_about = GtkMenuItem(label="About")
        # help_test.connect('activate', self.testCurrent)

        fm.append(file_new_win)
        fm.append(file_close_win)
        fm.append(file_exit)
        nm.append(nav_forward)
        nm.append(nav_backward)
        hm.append(help_about)

        fileMenu.set_submenu(fm)
        navMenu.set_submenu(nm)
        helpMenu.set_submenu(hm)
        return [fileMenu, navMenu, helpMenu]


######################### MAIN CODE #########################################
GLOBAL_WINDOW_COUNT = 0
x = GopherGUI()
x.show()
mainloop()

