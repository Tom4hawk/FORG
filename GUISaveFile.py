# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# This class asks users graphically which filename they'd like to save certain
# files into.  This is generally used for downloaded files that don't have
# associations bound to them, and that also can't be displayed, because
# they're binary data or otherwise ugly to look at as text.  :)  (e.g.
# *.zip, *.tar.gz, *.tgz, binhex, etc.
#
# Since this is a last resort, this module will try to import the Python
# Imaging Library (PIL) to display images if it is present.  Note that this
# requires that there be no association for the image files, since if there
# is, it won't even get as far as creating a GUISaveFile object to display.
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
from tkinter import *
from gopher import *
import os
import tkinter.filedialog
import Pmw
import re
import Options

import ContentFrame
import GopherResource
import GopherResponse
import Dialogs

try:
    import PIL
    from PIL import Image
    from PIL import ImageTk
except:
    print("Bummer dude!  You don't have the PIL installed on your machine!")
    print("That means that the \"Use PIL\" option is going to be irrelevant")
    print("for you.")

class PILImage(Label):
    # This was borrowed and adapted from the PIL programming examples.
    def __init__(self, master, im):
        if im.mode == "1":
            # bitmap image
            self.image = ImageTk.BitmapImage(im, foreground="white")
            Label.__init__(self, master, image=self.image, bg="black", bd=0)
        else:
            # Photo image object would be better...
            self.image = ImageTk.PhotoImage(im)
            Label.__init__(self, master, image=self.image, bd=0)

class GUISaveFile(ContentFrame.ContentFrame, Frame):
    verbose = None
    
    def __init__(self, parent_widget, parent_object, resp, resource, filename):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.r1 = None
        self.r2 = None
        self.filename = filename[:]
        self.parent = parent_object
        self.response = resp
        self.resource = resource

        # Don't even try to use the PIL unless the option is set
        # to allow it.
        usePIL = Options.program_options.getOption("use_PIL")

        if usePIL and self.canDisplay():
            try:
                self.packImageContent()
            except Exception as errstr:
                self.packSaveContent()
        else:
            self.packSaveContent()
            print("Packed save content")
        return None

    def packImageContent(self, *args):
        self.createPopup()
        self.image = Image.open(self.filename)
        self.scrframe = Pmw.ScrolledFrame(self)
        imgwidget = PILImage(self.scrframe.interior(), self.image)
        imgwidget.pack()
        imgwidget.bind('<Button-3>', self.popupMenu)
        self.scrframe.pack(fill='both', expand=1)
        
        # Return and DON'T display the save file as box only if the
        # file had no problems.  Otherwise an exception was raised.
        return None

    def revertToSaveDialog(self, *args):
        self.scrframe.pack_forget()     # Unpack the scrolled frame
        self.scrframe = None            # Lose the ref to the scrolled frame
        self.image    = None            # Lose the ref to the image object.
        self.packSaveContent()          # Go back to the "Save File" content
        self.pack_content()
        return None

    def imageInfo(self, *args):
        try:
            if not self.image:
                return None
        except:
            return None
        
        info = "Bands: %s" % self.image.getbands().join(", ")
        size = self.image.size
        info = "%s\nWidth: %d pixels\nHeight: %d pixels" % (info,
                                                            size[0], size[1])
        info = "%s\nMode: %s" % (info, self.image.mode)

        for key in list(self.image.info.keys()):
            info = "%s\n%s = %s" % (info, key, self.image.info[key])
        
            d = Dialogs.ErrorDialog(self, errstr=info,
                                    title='Image Information (PIL)')
        return None

    def createPopup(self):
        """Pop-up menu on right click on a message"""
        self.popup = Menu(self)
        self.popup['tearoff'] = FALSE
        self.popup.add_command(label='Save',
                               command=self.revertToSaveDialog)
        self.popup.add_command(label='Info',
                               command=self.imageInfo)

    def popupMenu(self, event):
        """Display pop-up menu on right click on a message"""
        self.popup.tk_popup(event.x_root, event.y_root)

    def canDisplay(self):
        try:
            fn = Image.open
        except:
            return None
            
        s = self.filename
        ind = s.rfind(".")
        
        if ind != -1 and ind != (len(s)-1):
            fileExtension = s[ind:].lower()

        return 1
            
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        self.parent.genericError("Error: Save Dialogs\n" +
                                 "are not searchable.")
        return None

    def pack_content(self, *args):
        return None
    
    def packSaveContent(self, *args):
        # Explicit copy - damn python and its ability to trip me up with all
        # that "everything's a reference" stuff.  :)
        default_filename = self.filename[:]

        for char in ['/', ':', ' ', r'\\']:
            strtofind = "%" + "%d;" % ord(char[0])
            default_filename = re.sub(strtofind, char, default_filename)

        for separator in ['/', ':', '\\']:
            ind = default_filename.rfind(separator)
            if ind != -1:
                default_filename = default_filename[ind+len(separator):]
                break

        if self.useStatusLabels:
            labeltext = "%s:%d" % (self.resource.getHost(), int(self.resource.getPort()))
        
            if self.resource.getName() != '' and self.resource.getLocator() != '':
                label2 = "\"%s\" ID %s" % (self.resource.getName(),
                                           self.resource.getLocator())
            else:
                label2 = "    "

            if len(label2) > 50:
                label2 = label2[0:47] + "..."

            Label(self, text=labeltext).pack(expand=0, fill='x')
            Label(self, text=label2).pack(expand=0, fill='x')

            Label(self, text=" ").pack()  # Empty line.

        Label(self,
              text="Please enter a filename to save this file as:").pack()
        
        cframe = Frame(self)
        cframe.pack(expand=1, fill='both')
        Label(cframe, text="Filename:").pack(side='left')

        self.filenameEntry = Entry(cframe)
        self.filenameEntry.insert('end', default_filename)
        self.filenameEntry.pack(side='left', expand=1, fill='x')
        self.filenameEntry.bind("<Return>", self.save)
        Button(cframe, text="Browse", command=self.browse).pack(side='right')
        self.saveButton = Button(cframe, text="Save", command=self.save)
        self.saveButton.pack(side='right')

        return None
    
    def browse(self, *args):
        dir = os.path.abspath(os.getcwd())
        filename = tkinter.filedialog.asksaveasfilename(initialdir=dir)

        if filename:
            self.filenameEntry.delete(0, 'end')
            self.filenameEntry.insert('end', filename)

        return None
    def save(self, *args):
        filename = self.filenameEntry.get()

        try:
            fp = open(filename, "w")
            fp.write(self.response.getData())
            fp.flush()
            fp.close()
        except IOError as errstr:
            self.parent.genericError("Couldn't save file\n%s:\n%s" % (filename,
                                                                      errstr))
            return None

        if self.r1:
            self.r1.destroy()
        if self.r2:
            self.r2.destroy()
            
        self.r1 = Label(self, text="File successfully saved into").pack()
        self.r2 = Label(self, text=filename).pack()
        return None
