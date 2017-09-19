# AssociationsEditor.py
# $Id: AssociationsEditor.py,v 1.8 2001/07/06 03:06:41 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# This pops up a dialog box and allows the user to associate file name
# extensions with various programs to run.
#
# It returns an Associations object, and can optionally take one as an
# argument.
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

import Associations
from gopher       import *
from Tkinter      import *
import Pmw
from string import *

class AssociationsEditor:
    DELIMITER = Associations.Associations.DELIMITER
    def __init__(self, parent, baseAssoc=Associations.Associations()):
        self.parent = parent
        self.dialog = Pmw.Dialog(parent, title='Edit Associations',
                                 buttons=('OK', 'Cancel'), defaultbutton='OK',
                                 command=self.dispatch)
        self.assoc = baseAssoc
        self.frame = self.dialog.interior()
        self.frame.pack(expand=1, fill='both')
        self.left_side  = Frame(self.frame)
        self.middle     = Frame(self.frame)
        self.right_side = Frame(self.frame)

        self.left_side.pack(side='left', expand=1, fill='both')
        self.middle.pack(side='left', expand=1, fill='both')
        self.right_side.pack(side='left', expand=1, fill='both')

        # Left side widgets
        inputbox = Frame(self.left_side)
        inputbox.grid(row=0, col=0, columnspan=2, rowspan=2, sticky=W)

        # File extension entry box and label.
        ftlabel = Label(inputbox, text='File extension:')
        self.ftEntry = Entry(inputbox, width=6)
        ftlabel.grid(row=0, col=0, sticky=W)
        self.ftEntry.grid(row=0, col=1, sticky=W)

        # Application entry box and label
        applabel = Label(inputbox, text='Application:')
        self.appEntry = Entry(inputbox, width=30)
        applabel.grid(row=1, col=0, sticky=W)
        self.appEntry.grid(row=1, col=1, sticky=W)

        # Instruction group box.
        group = Pmw.Group(self.left_side, tag_text='Instructions:')
        group.grid(row=2, column=0, rowspan=2, columnspan=2, sticky=W)
        instr1 = Label(group.interior(),
                       text='When entering in programs associated with files,')
        instr2 = Label(group.interior(),
                       text='Use $1 to represent the file being launched')
        instr3 = Label(group.interior(),
                       text='Filename extensions may be provided with or')
        instr4 = Label(group.interior(),
                       text='dots.  I.e. ".html" is the same as "html"')
        instr5 = Label(group.interior(),
                       text="Example: .html might be associated with")
        instr6 = Label(group.interior(),
                       text="netscape $1")
        instr7 = Label(group.interior(),
                       text=" ")
        instr8 = Label(group.interior(),
                       text="Extensions are case-sensitive")
        instr1.pack(side='top')
        instr2.pack(side='top')
        instr3.pack(side='top')
        instr4.pack(side='top')
        instr5.pack(side='top')
        instr6.pack(side='top')
        instr7.pack(side='top')
        instr8.pack(side='top')
        
        # Middle widgets
        self.addAssociationButton    = Button(self.middle, text='Add',
                                              command=self.add)
        self.removeAssociationButton = Button(self.middle, text='Remove',
                                              command=self.remove)
        self.setDefaultsButton       = Button(self.middle, text='Defaults',
                                              command=self.resetAssociations)
        # self.addAssociationButton.pack(side='top', expand=1, fill='both')
        # self.removeAssociationButton.pack(side='bottom', expand=1, fill='both')
        self.addAssociationButton.grid(row=0, col=0, sticky='NEW')
        self.removeAssociationButton.grid(row=1, col=0, sticky='NEW')
        self.setDefaultsButton.grid(row=2, col=0, sticky='NEW')
        
        # Right side widgets
        self.associationList = Pmw.ScrolledListBox(self.right_side,
                                                   hscrollmode='dynamic',
                                                   vscrollmode='static',
                                                   labelpos='nw',
                                                   dblclickcommand=self.reIns,
                                                   label_text='Associations:')
        self.associationList.pack(expand=1, fill='both')
        self.setAssociations(self.assoc)

        # self.dialog.activate()   # Make the dialog modal so the user can't
        #                          # mess with things in the other window.

    def resetAssociations(self, *args):
        self.setAssociations(self.assoc)

    def reIns(self, *args):
        selected = self.associationList.getcurselection()
        selected = selected[0]
        index = find(selected, self.DELIMITER)
        extension = selected[0:index]
        pgm = selected[index+len(self.DELIMITER):]

        self.ftEntry.delete(0, 'end')
        self.appEntry.delete(0, 'end')
        self.ftEntry.insert('end', extension)
        self.appEntry.insert('end', pgm)
        
        return None

    def extensionToAssociationExtension(self, ext):
        if len(ext) > 0:
            if ext[0] == '.':
                return ext[1:]
            else:
                return ext
        return ext
        
    def add(self, *args):
        extension = self.extensionToAssociationExtension(self.ftEntry.get())
        pgm       = self.appEntry.get()

        # Set the contents of the entry boxes back to nothing so the user
        # doesn't have to delete the contents before adding another association
        self.appEntry.delete(0, 'end')
        self.ftEntry.delete(0, 'end')

        str = extension + self.DELIMITER + pgm

        items = self.associationList.get()

        addItem = 1

        # Check to see if this entry is already in there somewhere.
        for x in range(0, len(items)):
            item = items[x]
            # If they have the same extension...
            if extension == item[0:len(extension)]:
                print "Replacing \"%s\"" % item
                # Remove it from the list.
                items = items[0:x-1] + (str,) + items[x+1:]
                addItem = None
                break

        if addItem:
            items = items + (str,)

        self.associationList.setlist(items)
        return None

    def remove(self, *args):
        self.associationList.delete('active')
        return None

    def setAssociations(self, assoc):
        list = ()
        
        for assocKey in assoc.getFileTypes():
            str = assocKey + self.DELIMITER + assoc.getProgramString(assocKey)
            list = list + (str,)

        self.associationList.setlist(list)
        return None

    def getAssociations(self, *args):
        self.assoc = Associations.Associations()

        for item in self.associationList.get():
            print "Got item %s" % item
            index = find(item, self.DELIMITER)
            extension = item[0:index]
            pgm = item[index+len(self.DELIMITER):]
            self.assoc.addAssociation(extension, pgm)
        
        return self.assoc
    
    def dispatch(self, button):
        if button == 'OK':
            assocs = self.getAssociations()
            self.parent.setAssociations(assocs)
            self.dialog.destroy()
            # Grab data and put it into an Assocations object.

        self.dialog.destroy()
        return None

