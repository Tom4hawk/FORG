# GUIAskForm.py
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
#
# The Tk/widget incarnation of AskForm
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

from Tkinter import *
from gopher import *
import Pmw
import ContentFrame
import GopherResource
import GopherResponse
import GopherConnection
import AskForm
import Question
import GUIQuestion

class GUIAskForm(ContentFrame.ContentFrame, Frame):
    verbose = None
    
    def __init__(self, parent_widget, parent_object, resp,
                 resource, filename=None, menuAssocs={}):
        Frame.__init__(self, parent_widget)  # Superclass constructor
        self.resource = resource
        self.response = resp
        self.parent   = parent_object
        self.filename = filename

        self.question_widgets = []
        self.questionBox = Pmw.ScrolledFrame(self,
                                             horizflex='fixed',
                                             vertflex ='fixed',
                                             hscrollmode='dynamic',
                                             vscrollmode='dynamic')
        return None
    
    def pack_content(self, *args):
        for x in range(0, self.response.questionCount()):
            q = self.response.nthQuestion(x)
            try:
                typename = questions_types["%s" % q.getType()]
            except KeyError:
                typename = "(ERROR NO TYPE)"
            print "PROCESSING Question %s %s %s" % (typename,
                                                    q.getDefault(),
                                                    q.getPromptString())
            try:
                wid = GUIQuestion.GUIQuestion(self.questionBox.interior(), q)
            except Exception, errstr:
                print "Couldn't make wid: %s" % errstr
                continue

            wid.grid(row=x, column=0, sticky=W)
            self.question_widgets.append(wid)

        self.submit = Button(self,
                             text="Submit", command=self.submit)
        self.questionBox.pack(side='top', expand=1, fill='both')
        self.submit.pack(side='bottom')
        return None
    
    def find(self, term, caseSensitive=None, lastIdentifier=None):
        self.parent.genericMessage("Sorry, AskForms are not searchable.\n" +
                                   "Or at least, not yet.")
        return None
    
    def submit(self, *args):
        """Submit the answers to the form questions to the server for
        processing, and load the results page."""
        values = []
        retstr = ""
        for widget in self.question_widgets:
            if widget.getType() == QUESTION_NOTE:
                continue
            values.append(widget.getResponse())
            retstr = "%s%s" % (retstr, widget.getResponse())

        print "Retstr is:\n%s" % retstr
        getMe = GopherResource.GopherResource()

        # Shouldn't cache this resource.
        getMe.setShouldCache(None)
        getMe.dup(self.resource)    # Copy defaults

        l = len(retstr)

        # Tell the server how much data we're sending...
        retstr = "+%d\r\n%s" % (l, retstr)
        
        getMe.setDataBlock(retstr)
        return self.parent.goElsewhere(getMe)
