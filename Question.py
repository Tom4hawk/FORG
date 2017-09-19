# Question.py
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
# $Id: Question.py,v 1.6 2001/07/11 22:43:09 s2mdalle Exp $
# Represents one question inside of a multi-question ASK block
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

from gopher import *
from string import *

QuestionException = "Error dealing with Question"

class Question:
    RESPONSE_ONE_LINE   = 1
    RESPONSE_PASSWORD   = 2
    RESPONSE_MULTI_LINE = 3
    RESPONSE_FILENAME   = 4
    RESPONSE_CHOICES    = 5
    verbose = None
    
    def __init__(self, data=""):
        self.qtype = None
        self.promptString = "%s%s" % ("Answer the nice man's question,\n",
                                      "and nobody gets hurt.")
        self.default      = ""
        self.setData(data)
        return None
    
    def getDefault(self):
        return self.default
    
    def setDefault(self, newdefault):
        self.default = newdefault
        return self.default
    
    def getPromptString(self):
        return self.promptString
    
    def getType(self):
        if self.verbose:
            print "QTYPE is ", self.qtype
        return self.qtype
    
    def setData(self, data):
        """Given data on a question in ASK format, this parses the data
        and sets the internal data of the object correctly.  This should be
        done pretty much first after creating the object."""
        
        self.linedata = data[:]   # Copy

        ind = find(data, ":")
        if ind == -1:
            raise QuestionException, "Cannot find \":\" on line"
        qtype = strip(data[0:ind])
        data = data[ind+1:]

        try:
            self.qtype = questions[qtype]
        except KeyError:
            raise(QuestionException,
                  "Question type \"%s\" is not valid" % qtype)
        
        # Do the rest here...
        if (self.qtype    == QUESTION_ASK
            or self.qtype == QUESTION_ASKL
            or self.qtype == QUESTION_ASKP):
            if find(data, "\t") != -1:
                try:
                    [promptStr, default_val] = split(data, "\t")
                except:
                    raise QuestionException, "Too many tabs in line"
                self.promptString = strip(promptStr)
                self.default = default_val
                if self.verbose:
                    print "Block has default of ", self.default
            else:
                self.promptString = strip(data)
        elif self.qtype == QUESTION_ASKP:
            pass
        elif (self.qtype    == QUESTION_ASKL
              or self.qtype == QUESTION_ASKF
              or self.qtype == QUESTION_CHOOSEF
              or self.qtype == QUESTION_NOTE):
            self.promptString = strip(data)
        elif self.qtype == QUESTION_CHOOSE or self.qtype == QUESTION_SELECT:
            try:
                ind = find(data, "\t")
                prompt = data[0:ind]
                opts = split(data[ind+1:], "\t")
            except :
                raise QuestionException, "Too many tabs in line"

            self.promptString = strip(prompt)
            self.options = opts
            self.default = self.options[0]
        else:
            raise QuestionException, "Unknown QType on parse"

        if self.verbose:
            print "Successfully parsed data line: ", self.linedata

        return None
