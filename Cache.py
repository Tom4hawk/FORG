# Cache.py
# $Id: Cache.py,v 1.14 2001/07/14 22:50:28 s2mdalle Exp $
# Written by David Allen <mda@idatar.com>
# Released under the terms of the GNU General Public License
#
# Handles cache-file related operations.
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
import os
import utils
import string
from gopher import *
from tkinter import *
import GopherResponse
import Pmw
import Options


class CacheException(Exception):
    def __init__(self, message):
        super(CacheException, self).__init__(message)


class Cache:
    verbose = None
    
    def __init__(self, *args):
        self._d = None

    def getCacheDirectory(self):
        try:
            dir = Options.program_options.getOption('cache_directory')
            return os.path.abspath(dir)
        except:
            return os.path.abspath("cache")

    def getCachePrefix(self):
        try:
            dir = Options.program_options.getOption('cache_prefix')
            return os.path.abspath(dir)
        except:
            return os.path.abspath("cache%scache" % os.sep)

    def getCacheStats(self):
        cdir = self.getCacheDirectory()
        
        [filecount, totalBytes, dircount] = utils.summarize_directory(cdir)

        kbcount = float(totalBytes)/float(1024)
        mbcount = kbcount/float(1024)

        kbcount = "%0.2fKB" % kbcount
        mbcount = "%0.2fMB" % mbcount

        datasize = "There is %s (%s) of data" % (kbcount, mbcount)
        fdcount  = "in %s files (%s directories total)" % (filecount, dircount)
        closer   = "underneath %s" % cdir

        return "%s\n%s\n%s" % (datasize, fdcount, closer)

    def emptyCache(self, parentTk):
        pref = self.getCachePrefix()
        
        self.dialog = Pmw.Dialog(parent=parentTk,
                                 title="Really delete cache?",
                                 buttons=('OK', 'Cancel'),
                                 defaultbutton='Cancel',
                                 command=self.__confirmDelete)
        
        fr = Frame(self.dialog.interior())
        fr.pack(side='top', fill='both', expand=1)

        lab1 = Label(fr, text="Are you sure you want to empty the cache?")
        lab2 = Label(fr, text="WARNING:  THIS WILL DELETE ALL FILES AND")
        lab3 = Label(fr, text="ALL SUBDIRECTORIES IN YOUR CACHE DIRECTORY,")
        lab4 = Label(fr, text="%s" % pref)
        lab5 = Label(fr, text=" ")
        lab6 = Label(fr, text="Continue?")

        lab1.grid(row=1, column=0, columnspan=5)
        lab2.grid(row=2, column=0, columnspan=5)
        lab3.grid(row=3, column=0, columnspan=5)
        lab4.grid(row=4, column=0, columnspan=5)
        lab5.grid(row=5, column=0, columnspan=5)
        lab6.grid(row=6, column=0, columnspan=5)
                                                
        # self.dialog.activate()

    def deleteCacheNoPrompt(self, *args):
        """Delete the cache without asking the user.  Do not do this unless
        you know what you're doing."""
        return self.__deleteCache()

    def __confirmDelete(self, button):
        if button != 'OK':
            self.dialog.destroy()
            return None

        self.dialog.destroy()   # Destroy the dialog anyway
        self.__deleteCache()    # Clean the files out
        return None
        
    def __deleteCache(self):
        pref = self.getCachePrefix()

        if not utils.dir_exists(pref):
            raise CacheException("Cache prefix %s doesn't exist." % pref)
                        
        cache_directories = os.listdir(pref)

        # I've been told that there's a shell utility module that does this
        # probably safer and better, but I'm not sure where it is, or whether
        # or not it's portable to crappy no-name 32 bit operating systems
        # out of Redmond, Washington.
        
        for item in cache_directories:
            item = "%s%s%s" % (pref, os.sep, item)
            if os.path.isdir(item):
                print("Recursively deleting \"%s\"" % item)
                utils.recursive_delete(item)
            else:
                print("Eh?  \"%s\" isn't a directory.  That's odd..." % item)

    def isInCache(self, resource):
        """Takes a resource, and returns true if the resource seems to have
        an available cache file associated with it, and None otherwise."""

        pref     = self.getCachePrefix()
        filename = resource.toCacheFilename()
        
        if pref[len(pref)-1] != os.sep and filename[0] != os.sep:
            # When joining together, separate paths with os.sep
            pref = "%s%s" % (pref, os.sep)

        # Now join together, and they will be properly joined.
        filename = pref + filename

        try:
            info = os.stat(os.path.abspath(filename))
            return [os.path.abspath(filename), info[6]]
        except OSError:
            return None
        return None
        
    def uncache(self, resource):
        """Takes a resource, and returns either None if the given resource
        is not cached on disk, or it returns a GopherResponse corresponding
        to what would have been gotten if it had been fetched from the
        server."""

        pref = self.getCachePrefix()
        file = resource.toCacheFilename()

        if pref[len(pref)-1] != os.sep and file[0] != os.sep:
            # When joining together, separate paths with os.sep
            pref = "%s%s" % (pref, os.sep)
            
        filename = pref + file
        
        try:
            # See if the file exists...
            tuple = os.stat(filename)
            if self.verbose:
                print("File %s of size %d exists." % (filename, tuple[6]))
        except OSError:
            # The file doesn't exist, we can't uncache it.
            return None

        print("===> Uncaching \"%s\"" % filename)
        resp = GopherResponse.GopherResponse()
        resp.setType(resource.getTypeCode())
        resp.setHost(resource.getHost())
        resp.setPort(resource.getPort())
        resp.setLocator(resource.getLocator())
        resp.setName(resource.getName())
        
        try:
            fp = open(filename, "r")

            # Consider reworking this somehow.  Slurp the entire file into
            # buffer.
            buffer = fp.read()
            fp.close()

            try:
                resp.parseResponse(buffer)
                resp.setData(None)
                # print "Loaded cache is a directory entry."
            except:
                # print "Loaded cache is not a directory."
                resp.setData(buffer)
                
            # Got it!  Loaded from cache anyway...
            # print "UNCACHE found data for use."
            return resp       
        except IOError as errstr:
            raise CacheException("Couldn't read data on\n%s:\n%s" % (filename,
                                                                      errstr))

        # We failed.  Oh well...
        return None
    
    def cache(self, resp, resource):
        """Takes a GopherResponse and a GopherResource.  Saves the content of
        the response to disk, and returns the filename saved to."""

        if resource.isAskType():
            # Don't cache ASK blocks.  This is because if you do, the program
            # will interpret it as data, and put the question structure inside
            # a text box.   Plus, since these may be dynamic, caching could
            # lead to missing out on things.
            raise CacheException("Do not cache AskTypes.  Not a good idea.")
        
        basedir      = self.getCachePrefix()
        basefilename = resource.toCacheFilename()

        # Problem - basedir is our base directory, but basefilename contains
        # trailing filename info that shouldn't be part of the directories
        # we're creating.
        filenamecopy = basefilename[:]
        ind = filenamecopy.rfind(os.sep)
        
        # Chop off extra info so "/home/x/foobar" becomes "/home/x/foobar"
        # this is because make_directories will otherwise create foobar as
        # a directory when it's actually a filename
        filenamecopy = filenamecopy[0:ind]     

        # Create the directory structure where necessary
        utils.make_directories(filenamecopy, basedir)

        basedirlastchar = basedir[len(basedir)-1]
        if basedirlastchar == os.sep:
            filename = "%s%s" % (basedir, basefilename)
        else:
            filename = "%s%s%s" % (basedir, os.sep, basefilename)

        # print "Cache: caching data to \"%s\"" % filename
        
        try:
            fp = open(filename, "w")

            if resp.getData() is None:    # This is a directory entry.
                response_lines = resp.getResponses()
                # Each response line is a GopherResource
                # write them as if it was a file served by the gopher server.
                # that way it can be easily reparsed when loaded from the
                # cache.
                for response_line in response_lines:
                    fp.write(response_line.toProtocolString())

                # write the string terminator.  This isn't really needed
                # since it isn't data, but it helps fool our other objects
                # into thinking that it's dealing with data off of a socket
                # instead of data from a file.  So do it.
                fp.write("\r\n.\r\n") 
            else:
                fp.write(resp.getData())

            fp.flush()
            fp.close()
        except IOError as errstr:
            # Some error writing data to the file.  Bummer.
            raise CacheException("Couldn't write to\n%s:\n%s" % (filename, errstr))
        # Successfully wrote the data - return the filename that was used
        # to save the data into.  (Absolute path)
        return os.path.abspath(filename)
        

