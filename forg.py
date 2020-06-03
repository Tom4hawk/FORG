#!/usr/bin/python2.7
# FORG.py
# $Id: forg.py,v 1.15 2001/09/02 17:01:42 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
#
# This file contains the core FORG class, which handles most of the logic
# and content.  The actual GUI around it is handled by TkGui.py.
# Theoretically, you could replace TkGui with GtkGui and it would work, but
# not really, since you'd have to rewrite the Tkinter specific parts of
# GUI*.py
#
# This object is meant as a wrapper for other things that subclass ContentFrame
# This should simply be the object that is packed into the main GUI window
# and be a subclass of Tkinter.Frame.
#
# This object knows how to download resources and display them properly by
# using the other classes in the FORG.  It basically is just a shell of a
# Tkinter.Frame that contains the logic for using the right classes in the
# right way.  So without navigation, this contains all that is needed to
# implement the functionality in other programs using just this class (and of
# course the other things that it needs)
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
##############################################################################
# System wide imports
from tkinter   import *                # Tk interface
from string    import *                # String manipulation
from threading import *                # Threads
import Pmw                             # Python Mega Widgets
import os                              # Operating system stuff
import socket                          # Socket communication
import sys
import tkinter.filedialog

# Non-GUI FORG specific imports
from gopher import *
import utils
import GopherConnection
import AskForm
import GopherResource
import GopherResponse
import Cache
import Options
import Associations
import List
import ListNode
import State

# GUI Specific
import GUIAskForm
import GUIDirectory
import GUIError
import GUIFile
import GUIQuestion
import GUISaveFile
import GUISearch
import ResourceInformation
import Dialogs

#--------------------------- VERSION ------------------------------------
VERSION = '0.6.0'
#--------------------------- VERSION ------------------------------------

class FORGException(Exception):
    def __init__(self, message):
        super(FORGException, self).__init__(message)


def getVersion():
    return VERSION


class FORG(Frame):
    verbose = None
    
    def __init__(self, parent_widget, resource, response=None,
                 messageBar=None,
                 parent_object=None):
        Frame.__init__(self, parent_widget)
        self.parent_widget = parent_widget
        self.parent_object = parent_object
        self.response      = response
        self.resource      = resource
        self.mb            = messageBar
        self.opts          = Options.program_options  # Global alias

        self.locations      = List.List()
        self.navList        = List.List()

        self._createPopup()
        
        self.currentContent = None

        # Go wherever the user intended us to go.
        self.goElsewhere(resource)
        
        return None
    def getCache(self):
        """Return the cache object being used"""
        return Options.program_options.getCache()
    def getMessageBar(self):
        """Return the message bar being used."""
        return self.mb
    def setMessageBar(self, newmb):
        """Set the message bar object."""
        self.mb = newmb
        return self.getMessageBar()

    def dumpQueue(self, *args):
        print("QUEUE IS:")
        def fn(node, s=self):
            r = node.getData().getResource()
            print(r.toURL())
            
        self.navList.traverse(fn)

    def stats(self, *args):
        buffer = "%s item(s) in the queue\n" % self.navList.countNodes()
        buffer = buffer + Options.program_options.cache.getCacheStats() + "\n"

        if self.verbose:
            print("QUEUE IS:")
            def fn(node, s=self):
                r = node.getData().getResource()
                print(r.toURL())
            
        self.navList.traverse(fn)
            
        self.genericMessage(buffer)
    
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        """This find method forwards all arguments to the child widget and
        does no processing.  See the documentation for ContentFrame.find for
        information on what parameters mean and what the method does."""
        # Pass on to the child verbatim.
        return self.child.find(term, caseSensitive, lastIdentifier)

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
    
    def getResource(self):
        """Returns the stored GopherResource object that was used to create
        this object."""
        return self.resource
    
    def getResponse(self):
        """Returns the stored GopherResponse object corresponding to the
        resource passed during the creation of this object"""
        return self.response

    def getGopherResponse(self):
        """This fetches the resource handed to the object from the network
        if necessary."""
        self.conn = GopherConnection.GopherConnection()
        msg = "Done"
        try:
            self.response = self.conn.getResource(resource=self.resource, msgBar=self.mb)
        except GopherConnection.GopherConnectionException as estr:
            raise FORGException(estr)
        except socket.error as err:
            try:
                if len(err) >= 2:
                    msg = "Can't fetch: errcode %d: %s" % (err[0], err[1])
                else:
                    msg = "Can't fetch: error %s" % err[0]
            except AttributeError:  # This is really weird, don't ask.
                msg =  "Can't fetch - unknown error."
            err = "getGopherResponse: %s" % err
            raise FORGException(err)

        if self.response.getError():
            raise FORGException(self.response.getError())

        # Turn the green light back on, since we're done with the transmission.
        self.opts.greenLight()
        return None

    def popupMenu(self, event):
        """Display pop-up menu on right click on a message"""
        self.popup.tk_popup(event.x_root, event.y_root)

    def saveFile(self, *args):
        """Pop up a dialog box telling the user to choose a filename to save
        the file as."""
        dir = os.path.abspath(os.getcwd())
        filename = tkinter.filedialog.asksaveasfilename(initialdir=dir)
        
        listNode = self.navList.getCurrent()
        response = listNode.getData().getResponse()

        if filename and filename != "":
            try:
                response.writeToFile(filename)
            except IOError as errstr:
                self.genericError("Couldn't write data to\n%s:\n%s" % (filename, errstr))

        return None

    def _createPopup(self):
        """Creates Pop-up menu on right click on a message"""
        self.popup = Menu(self)
        self.popup['tearoff'] = FALSE
        self.popup.add_command(label='Save', command=self.saveFile)
        self.popup.add_command(label='Back', command=self.goBackward)
        self.popup.add_command(label='Forward', command=self.goForward)

    def goForward(self, *rest):
        """Navigate forward"""
        try:
            node = self.navList.getNext()
            data = node.getData()

            # In case we are going forward to an error message...
            if not data.getResponse():
                # Remove current item in the list.
                self.navList.removeCurrent()

                # Go to this location again.
                return self.goElsewhere(data.getResource())

            self.createResponseWidget()
            self.changeContent(self.child)
        except List.ListException as errstr:
            if self.verbose:
                print("Couldn't get next: %s" % errstr)
        return None

    def goBackward(self, *rest):
        """Navigate backward."""
        try:
            node = self.navList.getPrev()
            state = node.getData()

            # In case we are going back to an error message...
            if not state.getResponse():
                # Remove current item in the list.
                self.navList.removeCurrent()

                # Go to this location again.
                return self.goElsewhere(state.getResource())

            self.response = state.getResponse()
            self.resource = state.getResource()
            self.createResponseWidget()
            node.setData(State.State(self.response, self.resource, self.child))
            self.changeContent(self.child)
        except List.ListException as errstr:
            if self.verbose:
                print("Couldn't get prev: %s" % errstr)

    def downloadResource(self, res):
        """Downloads the resource from the network and redisplays"""
        self.resource = res

        try:
            self.getGopherResponse()
        except FORGException as estr:
            self.genericError("Error fetching resource:\n%s" % estr)
            return None
            
        self.createResponseWidget()
        self.navList.insert(ListNode.ListNode(State.State(self.response,
                                                          self.resource,
                                                          self.child)))
        self.changeContent(self.child)
        return None

    def reload(self):
        newthread = Thread(group=None,
                           target=self.reloadResource,
                           name="Reload Thread",
                           args=())
        # Thread is responsible for adding the resource to the queue list
        # It will run and do its thing and when the function returns, the \
        # thread ends.
        newthread.start()
        return None

    def reloadResource(self):
        """Reloads from the network the current resource."""
        try:
            self.getGopherResponse()
        except FORGException as estr:
            self.genericError("Error fetching resource:\n%s" % estr)
            return None
        
        self.createResponseWidget()
        s = State.State(self.response, self.resource, self.child)
        self.navList.getCurrent().setData(s)
        self.changeContent(self.child)
        return None

    def getCurrentURL(self):
        return self.resource.toURL()
    
    def goElsewhere(self, resource, usecache=1, *args):
        """This is a wrapper for dealing with the download thread.  Pass it
        one resource as an argument, and that resource will be downloaded in
        the background.  Optionally, if the file exists in the cache, it will
        be loaded from there if usecache is true."""

        self.resource   = resource
        self.response   = None
        optionsUseCache = Options.program_options.getOption("use_cache")
        
        # Attempt to load the response object out of the cache.
        if usecache and optionsUseCache and not resource.getDataBlock():
            # Don't try to pull something out of cache unless it doesn't have
            # a data block. If it does, we have to submit information
            utils.msg(self.mb, "Looking for document in cache...")
            self.response = Options.program_options.cache.uncache(resource)

        if not self.response:
            utils.msg(self.mb,
                      "Document not in cache. Fetching from network.")
            # We need to fetch this document from the network.
            # Signal the download thread to go to work, and get out.
            newthread = Thread(group=None,
                               target=self.downloadResource,
                               name="Download Thread",
                               args=(self.resource,))
            # Thread is responsible for adding the resource to the queue list
            newthread.start()
            return
        else:
            utils.msg(self.mb, "Loading document from cache to display.")
            self.createResponseWidget()
            s = State.State(self.response, self.resource, self.child)
            self.navList.insert(ListNode.ListNode(s))
            self.changeContent(self.child)
        return None

    def changeContent(self, newwid):
        """Changes the current main content of the window to newwid"""
        if self.currentContent:
            self.currentContent.pack_forget()

        if newwid:
            utils.msg(self.mb, "Updating display...")            
            newwid.pack(expand=1, fill='both')
            newwid.pack_content()
            utils.msg(self.mb, "Done")

        self.currentContent = newwid

        try:
            self.parent_object.change_content_hook(self.getResource())
        except:
            # If it doesn't exist, or fails for some reason, that's the
            # parents problem, not ours.
            pass
        
        return self.currentContent
    
    def createResponseWidget(self):
        """Take the response already fetched and turn it into a child widget.
        This only works if the resource has already been fetched from the
        network."""
        
        if not self.response:
            raise(FORGException,
                  "createResponseWidget: No valid response present")
        if not self.resource:
            raise(FORGException,
                  "createResponseWidget: No valid resource present")

        cfilename = None
        
        if self.opts.getOption('use_cache'):
            utils.msg(self.mb, 'Caching data...')
            cfilename = ''

            _resr = self.resource.shouldCache()
            _resp = self.response.shouldCache()
            
            if not self.resource.isAskType() and _resr and _resp:
                # Don't try to cache ASK blocks.  It will only throw an
                # exception since caching them isn't a very stellar idea.
                try:
                    cfilename = self.opts.cache.cache(resp=self.response,
                                                      resource=self.resource)
                except Cache.CacheException as exceptionstr:
                    self.genericError(exceptionstr)

        r = self.response

        if self.response.getTypeCode() == RESPONSE_INDEXS:
            self.child = GUISearch.GUISearch(parent_widget=self,
                                             parent_object=self,
                                             resp=self.response,
                                             resource=self.resource,
                                             filename=cfilename)
        elif self.response.__class__ == AskForm.AskForm:
            try:
                self.child = GUIAskForm.GUIAskForm(parent_widget=self,
                                                   parent_object=self,
                                                   resp=self.response,
                                                   resource=self.resource,
                                                   filename=cfilename)
            except Exception as errstr:
                print("******************************************************")
                print("Caught ", Exception, " with error ", errstr, " ASK")
                self.child = Label(self, text="Congrats!  You've found a bug!")
        elif r.getData() is not None and not r.looksLikeDir(r.getData()):
            if cfilename is not None:
                assoc = self.opts.associations.getAssociation(cfilename)
                
                if assoc is not None:
                    self.LAUNCH_ME = [cfilename, assoc]
                    
            if self.response.getTypeCode() == RESPONSE_FILE:
                self.child = GUIFile.GUIFile(parent_widget=self,
                                             parent_object=self,
                                             resp=self.response,
                                             resource=self.resource,
                                             filename=cfilename)
            else:
                self.child = GUISaveFile.GUISaveFile(parent_widget=self,
                                                     parent_object=self,
                                                     resp=self.response,
                                                     resource=self.resource,
                                                     filename=cfilename)

        else:  # There is no data, display a directory entry
            ma = {
                "Back"       : self.goBackward,
                "Forward"    : self.goForward,
                "About FORG" : self.about }
                
            self.child = GUIDirectory.GUIDirectory(parent_widget=self,
                                                   parent_object=self, 
                                                   resp=self.response,
                                                   resource=self.resource,
                                                   filename=cfilename,
                                                   menuAssocs=ma)

    def about(self, *args):
        """Display the about box."""
        Pmw.aboutversion(getVersion())
        Pmw.aboutcopyright('Copyright 2000, 2001')
        Pmw.aboutcontact(
            'This program is licensed under the GNU General Public License\n' +
            'For more information, please see\n' +
            'http://www.gnu.org/')
        self._about_dialog = Pmw.AboutDialog(self, applicationname='FORG')
        # self._about_dialog.show()
        return None


################################### MAIN CODE ###############################

if __name__ == '__main__':
    # Require TkGui only if we are running the application stand-alone.
    from TkGui import *

    print("Starting the FORG")

    arr = sys.argv
    
    def main(item):
        try:
            app = TkGui(item)
            app.mainloop()
        except KeyboardInterrupt:
            app.quit()
            exit()

    url = ""

    try:
        url = arr[1]
        if (url[:]).lower().find("gopher://") == -1:
            url = "gopher://" + url
    except:
        url = None


    # Start the program
    print("Starting program with \"%s\"" % url)
    main(url)

