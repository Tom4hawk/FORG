# GUIDirectory.py
# $Id: GUIDirectory.py,v 1.27 2001/07/11 22:43:09 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# Graphical representation of directory views.
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
########################################################################

from gopher import *
from Tkinter import *
import Pmw
from string import *

import GopherResource
import GopherResponse
import GopherConnection
import ContentFrame
import Cache
import Options
import ResourceInformation

class GUIDirectory(ContentFrame.ContentFrame, Frame):
    # Behavior controllers
    verbose         = None

    # Colors for various links.
    DEFAULT_COLOR   = BLACK
    FOUND_COLOR     = RED
    LINK_COLOR      = BLUE
    ACTIVE_COLOR    = RED

    # Constants for use with packing things in their correct locations.
    TYPE_COLUMN     = 0
    TYPE_SPAN       = 1
    NAME_COLUMN     = 1
    NAME_SPAN       = 3
    BLURB_COLUMN    = 1
    BLURB_SPAN      = 3
    
    CACHE_COLUMN    = 4
    CACHE_SPAN      = 1
    INFO_COLUMN     = 5
    INFO_SPAN       = 2
    HOSTPORT_COLUMN = 7
    HOSTPORT_SPAN   = 1

    def __init__(self, parent_widget, parent_object, resp,
                 resource, filename=None, menuAssocs={}):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.searchlist = []    # Searchable terms...
        self.parent = parent_object
        self.cursel = None
        self.resp   = resp
        self.resource   = resource
        self.menuAssocs = menuAssocs
        self.createPopup()

        pmsgbar = self.parent.getMessageBar()
        if pmsgbar:
            self.balloons = Pmw.Balloon(parent_widget,
                                        statuscommand=pmsgbar.helpmessage)
        else:
            self.balloons = Pmw.Balloon(parent_widget)

        if self.useStatusLabels:
            labeltext = "%s:%d" % (resource.getHost(), int(resource.getPort()))
        
            if resource.getName() != '' and resource.getLocator() != '':
                label2 = "\"%s\" ID %s" % (resource.getName(),
                                           resource.getLocator())
            else:
                label2 = "    "
            if len(label2) > 50:
                label2 = label2[0:47] + "..."
            
            Label(self, text=labeltext).pack(side='top', expand=0, fill='x')
            Label(self, text=label2).pack(side='top', expand=0, fill='x')

        self.scrolled_window = Pmw.ScrolledCanvas(self,
                                                  borderframe=1,
                                                  usehullsize=1,
                                                  hull_width=400,
                                                  hull_height=400,
                                                  hscrollmode='dynamic',
                                                  vscrollmode='dynamic')
        
        self.sbox = Frame(self.scrolled_window.interior())
        self.scrolled_window.create_window(0, 0, anchor='nw',
                                           window=self.sbox)
        self.sbox.bind('<Button-3>', self.framePopupMenu)
        self.scrolled_window.interior().bind('<Button-3>', self.framePopupMenu)

        # As very LAST thing, pack it in. 
        self.scrolled_window.pack(fill='both', expand=1)
        return None
        # End __init__

    def pack_content(self, *args):
        responses = self.resp.getResponses()

        def color_widget(event, self=self, *args):
            wid = event.widget
            wid.configure(foreground=self.ACTIVE_COLOR)
            return None

        # Rather than having to fetch a specified option each time through
        # the loop, fetch them all at the beginning, since they shouldn't
        # change while we're packing content into the window.
        tmpopts = Options.program_options
        info_in_directories = tmpopts.getOption("display_info_in_directories")
        show_host_port      = tmpopts.getOption("show_host_port")
        show_cached         = tmpopts.getOption('show_cached')

        for x in range(0, len(responses)):
            if x % 50 == 1:
                self.scrolled_window.resizescrollregion()
            
            r = responses[x]
            rname    = r.getName()
            rtype    = r.getType()
            
            l = Label(self.sbox, text=rtype)
            
            if r.getTypeCode() == RESPONSE_BLURB:
                # Some servers prefix blurbs that are not meant to be displayed
                # with (NULL).  Ferret these out, and just display a blank
                # line.
                if find(rname, "(NULL)") == 0:
                    rname = " "
                
                blurb_label = Label(self.sbox, foreground=self.DEFAULT_COLOR,
                                    text=rname)
                blurb_label.grid(row=x, columnspan=self.BLURB_SPAN,
                                 column=self.BLURB_COLUMN, sticky=W)
                self.searchlist.append([rname, blurb_label,
                                        self.DEFAULT_COLOR])
                
            else:
                # Trick Tk into passing arguments with the function and
                # get around Python's weird namespacing.
                def fn(event, self=self.parent, r=r, w=self, *args):
                    self.goElsewhere(r)
                    return None
                        
                def dopopup(event, resource=r, self=self):
                    # This binds resource to a parameter that
                    # one of several popup commands will use.
                    return self.popupMenu(event, resource)

                def enter_signal(event, resource=r,
                                 box=self.sbox, rowno=x, p=self):
                    host = resource.getHost()
                    port = resource.getPort()
                    resource.__blurb__ = Label(box,
                                               text=resource.toURL())
                    resource.__blurb__.grid(row=rowno,
                                            col=p.HOSTPORT_COLUMN,
                                            columnspan=p.HOSTPORT_SPAN,
                                            sticky=E)

                def leave_signal(event, resource=r):
                    try:
                        resource.__blurb__.destroy()
                    except:
                        pass
                
                # Don't make it clickable if it's an error.  But if it
                # isn't an error, connect these signals.
                if r.getTypeCode() != RESPONSE_ERR:
                    default_color = self.LINK_COLOR
                    b = Label(self.sbox, foreground=self.LINK_COLOR,
                              text=r.getName())
                    b.bind('<ButtonRelease-1>', fn)
                    b.bind('<Button-1>', color_widget)
                    b.bind('<Button-3>', dopopup)

                    if show_host_port:  # Cached option
                        b.bind('<Enter>', enter_signal)
                        b.bind('<Leave>', leave_signal)

                    # Attach a balloon
                    btext = r.toURL()
                    self.balloons.bind(b, None, btext)
                else:
                    default_color = self.DEFAULT_COLOR
                    b = Label(self.sbox, foreground=self.DEFAULT_COLOR,
                              text=rname)


                # Each entry in the searchlist is the name of a widget as a
                # string, the widget itself, and the widget's default color
                # The color is needed because 'finding' things requires
                # changing their color.
                self.searchlist.append([rname, b, default_color])
                
                l.grid(row=x,
                       column=self.TYPE_COLUMN,
                       columnspan=self.TYPE_SPAN,
                       sticky=W)
                b.grid(row=x,
                       column=self.NAME_COLUMN,
                       columnspan=self.NAME_SPAN,
                       sticky=W)

                cacheobj = self.parent.getCache()
                
                if info_in_directories:    # Cached option
                    if r.getInfo() != None:
                        i = r.getInfo()
                        t = i.getAdmin()
                        
                        if len(t) > 40:
                            t = t[0:40]
                            Label(self.sbox,
                                  text=t).grid(row=x,
                                               col=self.INFO_COLUMN,
                                               columnspan=self.INFO_SPAN)
                        else:
                            Label(self.sbox,
                                  text=t).grid(row=x,
                                               col=self.INFO_COLUMN,
                                               columnspan=self.INFO_SPAN)
                    else:
                        Label(self.sbox, text="  ").grid(row=x,
                                                    col=self.INFO_COLUMN,
                                                    columnspan=self.INFO_SPAN)

                # Possibly report to the user whether or not a given file is
                # present in cache.  I like to know this, but some people
                # don't, so make it a settable option.
                if show_cached:  # Cached option
                    if cacheobj.isInCache(r):
                        Label(self.sbox,
                              text="Cached").grid(row=x,
                                                  col=self.CACHE_COLUMN,
                                                  columnspan=self.CACHE_SPAN)
                    else:
                        Label(self.sbox,
                              text=" ").grid(row=x,
                                             col=self.CACHE_COLUMN,
                                             columnspan=self.CACHE_SPAN)

        self.scrolled_window.resizescrollregion()
        return None
        
    def destroy(self, *args):
        self.pack_forget()
        self.scrolled_window.destroy()
        Frame.destroy(self)
        return None

    def viewSource(self, *args):
        wintitle = "Source: %s" % self.resource.toURL()
        dialog   = Pmw.Dialog(self.parent, title=wintitle, buttons=())

        textwid = Pmw.ScrolledText(dialog.interior(), hscrollmode='dynamic',
                                   vscrollmode='static')
        textwid.insert('end', self.resp.toProtocolString())
        textwid.pack(expand=1, fill='both', side='top')
        return None

    def createPopup(self):
        """Pop-up menu on right click on a message"""
        self.popup = Menu(self)
        self.popup['tearoff'] = FALSE
        self.popup.add_command(label='Info', command=self.infoPopup)
        self.popup.add_command(label='Cache Status', command=self.cacheStatus)

        kz = self.menuAssocs.keys()
        kz.sort()
        
        for key in kz:
            self.popup.add_command(label=key,
                                   command=self.menuAssocs[key])

        self.framePopup = Menu(self)
        self.framePopup['tearoff'] = FALSE
        self.framePopup.add_command(label='View Directory Source',
                                    command=self.viewSource)

        for key in self.menuAssocs.keys():
            self.framePopup.add_command(label=key,
                                        command=self.menuAssocs[key])


    def popupMenu(self, event, item):
        """Display pop-up menu on right click on a message"""
        self.cursel = item
        self.popup.tk_popup(event.x_root, event.y_root)
        return None

    def framePopupMenu(self, event):
        self.framePopup.tk_popup(event.x_root, event.y_root)
        return None
    
    def cacheStatus(self, resource=None):
        c = self.parent.getCache()

        if resource is None:
            resource = self.cursel
            
        resp = c.isInCache(resource)

        if resp is None:
            str = "Resource\n%s\nis not in the cache." % resource.toURL()
            self.parent.genericMessage(str, "Cache Status")
        else:
            url = resource.toURL()
            [filename, size] = resp
            str = "%s\nis in the cache as\n%s\n and is %s bytes" % (url,
                                                                    filename,
                                                                    size)
            self.parent.genericMessage(str, "Cache Status")
        return None

    def infoPopup(self, resource=None):
        if resource is None:
            resource = self.cursel

        if not resource.isGopherPlusResource():
            # Info is only a valid operation if it's a Gopher+ resource.
            # Regular gopher servers don't provide any info in this way.
            str = "%s%s" % ("This item is not a Gopher+ Resource.\n",
                            "No special information is available about it.")
            self.parent.genericError(str, "Error:")
            return None
        
        if resource.getInfo() is None:
            try:
                conn = GopherConnection.GopherConnection()
                info = conn.getInfo(resource)
                resource.setInfo(info)
            except Exception, errstr:
                url = resource.toURL()
                str = "Cannot display information about\n%s:\n%s" % (url,
                                                                     errstr)
                self.parent.genericError(str, "Error:")
                return None

        info = resource.getInfo()
        str = "Resource information:\n%s\n%s" % (resource.toURL(),
                                                 info.toString())
        gri = ResourceInformation.GUIResourceInformation(info)
        return None
            
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        """Overrides the same definition in ContentFrame.ContentFrame"""

        if lastIdentifier is None:  # Note this is a distinct case from when 
            self.lastIndex = -1     # lastIdentifier is false (possibly 0)
        else:
            # This could be 0 or any positive number.
            self.lastIndex = lastIdentifier

        try:
            self.lastIndex = int(self.lastIndex) # Unstringify
        except:
            raise(Exception,
                  "Illegal last ID passed to %s.find()" % self.__class__)

        if self.verbose:
            print "LAST FOUND INDEX was %s." % self.lastIndex
        
        # Bounds checking on lastIndex...
        if self.lastIndex < -1 or self.lastIndex > len(self.searchlist):
            print "*****Something's messed up.  Bad lastIdentifier."
        elif self.lastIndex >= 0:
            [old_label, old_widget, color] = self.searchlist[self.lastIndex]
            old_widget.configure(foreground=color)

        found      = None
        foundIndex = -1
        
        for x in range(self.lastIndex+1, len(self.searchlist)):
            [label, label_widget, color] = self.searchlist[x]
            
            if self.verbose:
                print "Looking at index %d through \"%s\"..." % (x, label)
                
            if not caseSensitive:
                # If we're not doing case-sensitive compares, convert them
                # both to lower case and we'll compare them that way.
                label = lower(label)
                term  = lower(term)
                
            if find(label, term) != -1:
                # Term was found in this label
                foundIndex = x
                found = 1
                # Find only one match per call to this function.  Bail out.
                break

        if found:
            [found_label, found_widget, color] = self.searchlist[foundIndex]

            # A bit of explanation on what this is:
            # to scroll to the correct location in the window (so the user
            # can see what was found and highlighted) we need a certain
            # distance to scroll the bar.  Since directory entries are all
            # that's in the window, and there's one per line, this should
            # work.
            scrlratio = float(foundIndex) / float(len(self.searchlist))

            if self.verbose:
                print "Scrlratio is: \"%s\"" % scrlratio
                print "Found \"%s\" in \"%s\" at index %d" % (term,
                                                              found_label,
                                                              foundIndex)
                
            # Turn the one that was found into FOUND_COLOR
            found_widget.configure(foreground=self.FOUND_COLOR)

            # Scroll the window to scrlratio - this should place the found
            # item at the very top of the window.
            self.scrolled_window.yview('moveto', scrlratio)
            
            if self.verbose:
                print "RETURNING NEW FOUND INDEX: %s" % foundIndex
                
            return foundIndex
        else:
            return None  # This signals that it wasn't found, and to reset

        # Everything else this class needs gets inherited from other classes.
