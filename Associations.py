# Associations.py
# $Id: Associations.py,v 1.8 2001/07/11 22:43:09 s2mdalle Exp $
#
# Handles associations between file types and programs.
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
import re
import os
from string import *


class AssociationsException(Exception):
    def __init__(self, message):
        super(AssociationsException, self).__init__(message)


class Associations:
    verbose = None
    DELIMITER = " => "
    
    def __init__(self):
        self.dict    = {}
        self.threads = 0
        return None
    
    def addAssociation(self, suffix, pgm):
        """Adds an association to the list.  suffix holds the file
        extension, and pgm holds the name of the executing program.  Example
        is suffix=.jpg and pgm=gimp $1"""
        
        if suffix[0] == '.':
            suffix = suffix[1:]
        self.dict[suffix] = pgm
        return None

    def save(self, filename):
        """Saves associations to filename"""
        return self.writeToFile(filename)

    def writeToFile(self, filename):
        """Writes text representation to filename that can be loaded later"""
        fp = open(filename, "w")

        lines = ["FORG associations.  This is the mechanism that allows the",
                 "FORG to launch particular programs when dealing with",
                 "different file extensions.  The format is like this:",
                 "file_suffix%sprogram_to_launch" % self.DELIMITER,
                 "where file_suffix is something such as \".jpg\", etc.",
                 "program_to_launch is the command line of the program that",
                 "you want launched.  You may use $1 to represent the file",
                 "so to launch a HTML file, you might use:",
                 ".html%s/usr/X11/bin/netscape $1" % self.DELIMITER]

        map(lambda line,f=fp: f.write("# %s\n" % line),
            lines)

        for key in self.dict.keys():
            fp.write("%s%s%s\n" % (key, self.DELIMITER, self.dict[key]))
        fp.flush()
        fp.close()
        return 1

    def loadFromFile(self, filename):
        """Loads instance of Associations from filename"""
        fp = open(filename, "r")
        self.dict = {}
        
        for line in fp.readlines():
            line = strip(line)
            if len(line) > 0 and line[0] == '#':
                continue  # Skip comments.
            
            try:
                [key, value] = split(line, self.DELIMITER, 2)
                self.addAssociation(key, value)
            except:
                print "Error parsing line in associations file: %s" % line

        fp.close()
        return 1

    def isEmpty(self):
        return len(self.dict.keys()) == 0
    
    def getFileTypes(self):
        """Returns the file suffixes the Association list knows of"""
        return self.dict.keys()
    
    def getProgramString(self, key):
        try:
            ans = self.dict[key]
            return ans
        except KeyError:
            return None
        
    def getTmpFilename(self, suffix, *args):
        return foo + "." + suffix
        return None
    
    def removeAssociation(self, suffix):
        try:
            del(self.dict[suffix])
        except KeyError:
            pass
        
    def getAssociation(self, filename):
        """Given a particular filename, find the correct association
        for it, if any."""
        # Turn it into a real filename so some programs won't go stupid
        # on us and try to look up a partial URL in a filename, particularly
        # with cache filenames.
        # print "Finding assoc for %s" % filename
        filename = "." + os.sep + filename
        matchFound = None
        ind = len(filename)-1;
        while not matchFound and ind != -1:
            str   = filename[ind+1:]
            assoc = None
            try:
                assoc = self.dict[str]
            except:
                pass
            ind = rfind(filename, ".", 0, ind)
            if assoc:
                matchFound = 1

        if ind == -1 or not matchFound:
            # print "Couldn't find association for this filetype."
            return None

        # print "Found assoc %s for filename %s" % (assoc, filename)
        return assoc
    
    def applyAssociation(self, filename, assoc=None):
        """Given a filename and an association, execute the helper program
        in order to properly process the file."""
        
        if assoc == None:
            assoc = self.getAssociation(filename)

        if assoc == None or assoc == '':
            raise AssociationsException("No association found.")
        
        # Assoc holds the program name
        assoc = re.sub("$1", "\"" + filename + "\"", assoc, 1)
        fp = os.popen(assoc)
        print "Process dump: %s" % assoc
        try:
            while 1:
                line = fp.readline()
                if line == '':
                    break;
                print line
        except:
            print "Process %s exited with an exception." % assoc
            return None
        print "Process \"%s\" finished up and exited." % assoc
        return 1

    
