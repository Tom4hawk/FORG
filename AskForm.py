# AskForm.py
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
# $Id: AskForm.py,v 1.6 2001/04/07 19:12:44 s2mdalle Exp $
# An AskForm is essentially a conglomeration of Question objects.
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
#########################################################################

from string import *
import GopherResponse
import Question

class AskForm(GopherResponse.GopherResponse):
    def __init__(self, askformdata=""):
        GopherResponse.GopherResponse.__init__(self)
        self.questions = []
        self.setAskFormData(askformdata)
        return None
    def questionCount(self):
        return len(self.questions)
    def nthQuestion(self, nth):
        return self.questions[nth]
    def setAskFormData(self, data):
        self.data = data

        print("ASKFORM:  Parsing data block:\n", data)
        self.lines = split(self.data, "\n")

        for line in self.lines:
            line = strip(line)
            if line == '' or line == '.':
                continue
            try:
                q = Question.Question(line)
            except Question.QuestionException as qstr:
                print("Error parsing question \"%s\": %s" % (line, qstr))
                continue
            
            self.questions.append(q)
