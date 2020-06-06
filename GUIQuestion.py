# GUIQuestion.py
# $Id: GUIQuestion.py,v 1.13 2001/07/02 22:50:39 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
#
# A GUI representation of a question.  It should provide all methods needed
# to get the response, set default values, etc.
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
#############################################################################

from tkinter import *
import Pmw
import tkinter.filedialog
from string import *
from gopher import *
import GopherResource
import GopherResponse
import GopherConnection
import ContentFrame
import Cache
import Options
import Question

GUIQuestionException = "Sorry.  Things just sometimes go wrong."

class GUIQuestion(Frame):
    verbose = None

    def __init__(self, parent_widget, question):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.parent = parent_widget
        self.question = question
        self.type     = self.question.getType()

        promptString = self.question.getPromptString()
        defaultValue = self.question.getDefault()

        Label(self, text=promptString).grid(row=0, column=0, sticky=W)

        if self.type == QUESTION_NOTE:
            # Prompt string is all we need for this one.
            return None

        if self.type == QUESTION_ASK:
            self.entry = Entry(self)
            if len(defaultValue) > 0:
                self.entry.insert('end', defaultValue)
            self.entry.grid(row=0, column=1, columnspan=4, sticky=W)
            return None
        if self.type == QUESTION_ASKF or self.type == QUESTION_CHOOSEF:
            self.entry = Entry(self)
            if len(defaultValue) > 0:
                self.entry.insert('end', defaultValue)
            self.entry.grid(row=0, column=1, columnspan=4, sticky=W)

            # Browse buttons for file selection.
            self.browse = Button(text="Browse", command=self.browse)
            self.browse.grid(row=0, column=5, sticky=W)
            return None
        if self.type == QUESTION_ASKP:
            self.entry = Entry(self, show="*")

            if len(defaultValue) > 0:
                self.entry.insert('end', defaultValue)
            self.entry.grid(row=0, column=1, columnspan=4, sticky=W)
            return None
        if self.type == QUESTION_ASKL:
            self.entry = Pmw.ScrolledText(self, hscrollmode='dynamic',
                                          text_width=80, text_height=6,
                                          vscrollmode='dynamic')
            self.entry.grid(row=1, column=0, columnspan=2, rowspan=2,
                            sticky='N')
            return None
        if self.type == QUESTION_SELECT:
            self.entry = Pmw.RadioSelect(self, buttontype='checkbutton',
                                         command=self.changed)
            
            for opt in self.question.options:
                self.entry.add(opt)
                
            if defaultValue:
                print("Invoking defalut %s" % defaultValue)
                self.entry.invoke(defaultValue)

            self.entry.grid(row=1, column=0, columnspan=4, rowspan=4,
                            sticky='NSEW')
            print('Returning SELECT GUIQuestion')
            return None
        if self.type == QUESTION_CHOOSE:
            self.entry = Pmw.RadioSelect(self, buttontype='radiobutton',
                                         command=self.changed)
            for opt in self.question.options:
                self.entry.add(opt)
            if defaultValue:
                print("Invoking defalut %s" % defaultValue)
                self.entry.invoke(defaultValue)
                
            self.entry.grid(row=1, column=0, columnspan=4, rowspan=4,
                            sticky='NSEW')
            print("Returning CHOOSE GUIQuestion")
            return None
        return None
    def browse(self, *args):
        dir = os.path.abspath(os.getcwd())
        filename = tkinter.filedialog.asksaveasfilename(initialdir=dir)
        self.entry.delete(0, 'end')
        if filename:
            self.entry.insert('end', filename)
        return None
    def getType(self):
        return self.question.getType()
    def changed(self, *args):
        print("Selection changed:  Current selection:  ", args)
    def getResponse(self):
        """Returns the current state of the widget, or what should be sent
        to the server."""
        if self.entry.__class__ == Entry:
            return "%s\n" % self.entry.get()
        elif self.entry.__class__ == Pmw.ScrolledText:
            buf = self.entry.get()
            lines = count(buf, "\n")
            return "%d\n%s\n" % (lines, buf)
        elif self.entry.__class__ == Pmw.RadioSelect:
            list = self.entry.getcurselection()
            return "%s\n" % list[0]
        else:
            # Huh?  What?  Eh?  WTF is going on?
            raise GUIQuestionException("Cannot get content: Unknown type")
        return ""

        
