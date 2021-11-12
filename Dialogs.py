# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Contains many different program dialogs used for information and data
# entry purposes.
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
import tkinter as tk
from types import *
import Pmw
from Bookmarks.Bookmark import Bookmark
from tkui.Dialog import Dialog


class FindDialog:
    def __init__(self, parent, searchwidget, parentobj=None, *args):
        self.parent = parent
        self.parentobj = parentobj
        self.searchwidget = searchwidget

        self.dialog = Dialog(title='Find Text...',
                                 buttons=('OK', 'Cancel'), default_button='OK',
                                 command=self.dispatch)

        self.frame = tk.Frame(self.dialog.interior())
        self.frame.pack(expand=1, fill='both')

        tk.Label(self.frame, text="Find a term...").grid(row=0, column=0, columnspan=5)
        tk.Label(self.frame, text="Term: ").grid(row=1, column=0)

        self.searchEntry = tk.Entry(self.frame, text="")
        self.searchEntry.grid(row=1, column=1, columnspan=4)

        self.css = tk.IntVar()
        
        self.caseSensitiveCheckBox = tk.Checkbutton(self.frame,
                                                 text="Case-sensitive search",
                                                 variable = self.css,
                                                 command  = self.cb)
        self.caseSensitiveCheckBox.grid(row=2, column=0, columnspan=4)
        
        self.lastMatch = None
        # self.dialog.activate()

    def cb(self, *args):
        # print "Var is ", self.css.get()
        return None
    
    def getSearchTerm(self):
        """Returns the search term currently in the search box."""
        return self.searchEntry.get()
    
    def getCaseSensitive(self):
        """Returns the status of the case sensitive check button"""
        return self.css.get()
    
    def dispatch(self, button):
        """Handles button clicking in the dialog.  (OK/Cancel)"""
        if button != 'OK':
            # Smack...
            self.dialog.destroy()
            return None

        # Otherwise, go look for a term...
        # try:
        self.lastMatch = self.searchwidget.find(self.getSearchTerm(), self.getCaseSensitive(), self.lastMatch)
        
        print("Last match is now ", self.lastMatch)
        return self.lastMatch

class OpenURLDialog:
    def __init__(self, parentwin, callback):
        self.callback = callback
        self.dialog   = Pmw.Dialog(parentwin, title="Open URL:",
                                   command=self.dispatch,
                                   buttons=('OK', 'Cancel'),
                                   defaultbutton='OK')
        i = self.dialog.interior()
        tk.Label(i, text="Enter URL to Open:").pack(side='top', expand=1, fill='both')
        self.urlEntry = tk.Entry(i, width=30)
        self.urlEntry.insert('end', "gopher://")
        self.urlEntry.pack()
        
    def dispatch(self, button):
        if button == 'OK':
            # If OK is clicked, fire the callback with whatever the URL
            # happens to be.
            self.callback(self.urlEntry.get())

        # In any case, destroy the dialog when finished.
        self.dialog.destroy()
        return None
    

class NewBookmarkDialog:
    def __init__(self, parentwin, cmd, resource=None):
        self.cmd = cmd
        self.dialog = Dialog(parent=parentwin, title="New Bookmark:", command=self.callback, buttons=('OK', 'Cancel'))
        interior = self.dialog.interior()
        namebox = tk.Frame(interior)
        urlbox = tk.Frame(interior)
        tk.Label(interior, text="Enter Bookmark Information:").pack(side='top', expand=1, fill='both')
        namebox.pack(fill='both', expand=1)
        urlbox.pack(fill='both', expand=1)
        
        tk.Label(namebox, text="Name:").pack(side='left')
        self.nameEntry = tk.Entry(namebox, width=30)
        self.nameEntry.pack(side='right', fill='x', expand=1)
        tk.Label(urlbox, text="URL:").pack(side='left')
        self.URLEntry = tk.Entry(urlbox, width=30)
        self.URLEntry.pack(side='right', fill='x', expand=1)

        if resource:
            self.URLEntry.insert('end', resource.toURL())
            self.nameEntry.insert('end', resource.getName())

    def callback(self, button):
        if button and button != 'Cancel':
            res = Bookmark()
            res.setURL(self.URLEntry.get())            
            res.setName(self.nameEntry.get())
            self.cmd(res) # Do whatever our parent wants us to with this...

        self.dialog.destroy()


class NewFolderDialog:
    BUTTON_OK     = 0
    BUTTON_CANCEL = 1
    
    def __init__(self, parentwin, callback, folderName=None):
        self.buttons = ('OK', 'Cancel')
        self.callback = callback
        self.parent   = parentwin
        self.dialog = Dialog(parent=parentwin, title="New Folder:", command=self.closeDialog, buttons=self.buttons)

        i = self.dialog.interior()
        tk.Label(i, text="New Folder Title:").grid(row=0, column=0, sticky='EW')
        self.__entry = tk.Entry(i)
        self.__entry.grid(row=1, column=0, sticky='EW')
        
        if folderName:
            self.__entry.insert('end', folderName)
            
        self.bindCallbacks()

    def bindCallbacks(self):
        self.__entry.bind('<Return>', self.closeDialog)

    def closeDialog(self, result):
        if result == self.buttons[self.BUTTON_CANCEL]:
            self.dialog.destroy()
            return None
        else:
            str = self.__entry.get()
            self.dialog.destroy()
            return self.callback(str)
    # End NewFolderDialog
    
class InformationDialog:
    def __init__(self, parent, error_msg: str, title: str = 'Information:'):
        # We don't need an activate command since we want the dialog to just
        # get smacked when the user presses close.
        if title == '':
            title = error_msg
        self.dialog = Dialog(parent=parent, title=title, buttons=["Close"])

        # print "========================================================"
        # print "Error Dialog: %s" % errstr
        # print "========================================================"

        if type(error_msg) != str:
            error_msg = str(error_msg)

        labels = error_msg.split("\n")
        
        for label in labels:
            tk.Label(self.dialog.interior(), text=label).pack(side='top')

        # self.dialog.activate() # Modalize  :)


class ErrorDialog(InformationDialog):
    def __init__(self, parent, error_msg: str, title: str = "Error:"):
        InformationDialog.__init__(self, parent, error_msg, title)



