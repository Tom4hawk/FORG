# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Random functions used in many places that don't belong together in an
# object.
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
import os
import stat

def summarize_directory(dirname):
    """Returns an array [x, y, z] where x is the number of files in all subdirs
    of dirname and y is the total summed size of all of the files and z is
    the total number of directories."""

    filecount  = 0
    summedSize = 0
    dircount   = 0
    
    files = os.listdir(dirname)
    for file in files:
        if file == '.' or file == '..':
            continue
        
        path = os.path.join(dirname, file)
        if os.path.isdir(path):
            dircount = dircount + 1     # Discovered a new directory
            [tfc, tfs, tdc] = summarize_directory(path)
            # Add whatever came back from the recursive call.
            filecount  = filecount + tfc
            summedSize = summedSize + tfs
            dircount   = dircount + tdc
        else:
            filecount = filecount + 1
            statinfo  = os.stat(path)
            summedSize = summedSize + statinfo[stat.ST_SIZE]

    return [filecount, summedSize, dircount]

def file_exists(filename):
    try:
        os.stat(filename)
    except OSError:
        return None

    return 1

def recursive_delete(dirname):
    """Runs the equivalent of an rm -rf on a given directory.  Does not make
    any distinction between symlinks, etc. so use with extreme care.
    Thanks to comp.lang.python for tips on this one..."""
    files = os.listdir(dirname)
    for file in files:
        if file == '.' or file == '..':
            # The calls used to find filenames shouldn't ever return this,
            # but just in case, we check since this would be horrendously
            # bad.
            continue
        
        path = os.path.join(dirname, file)
        if os.path.isdir(path):
            recursive_delete(path)
        else:
            print('Removing file: "%s"' % path)
            retval = os.unlink(path)

    print('Removing directory:', dirname)
    os.rmdir(dirname)
    return 1

def character_replace(str, findchar, replacechar):

    if findchar is replacechar or findchar == replacechar:
        # That's a no-no...
        raise Exception("character_replace: findchar == replacechar")

    ind = str.find(findchar)

    while ind != -1:
        str = str[0:ind] + "%s" % replacechar + str[ind+1:]
        ind = str.find(findchar)
    return str

def dir_exists(dirname):
    try:
        stat_tuple = os.stat(dirname)
    except OSError:
        return None
    return stat.S_ISDIR(stat_tuple[0])

def make_directories(path, basedir):
    """Makes path directories off of basedir.  Path is a relative path,
    and basedir is an absolute path.  Example of invocation:
    make_directories('foo/bar/baz/quux', '/home/user/') will ensure that
    the path /home/user/foo/bar/baz/quux exists"""
    arr = path.split(os.sep)

    if basedir[len(basedir)-1] == os.sep:
        # Trim tailing dir separator
        basedir = basedir[0:len(basedir)-1]

    if not dir_exists(basedir):
        os.mkdir(basedir)

    for item in arr:
        if not item or item == '':
            continue
        dirname = "%s%s%s" % (basedir, os.sep, item)

        if not dir_exists(dirname):
            os.mkdir(dirname)
            
        basedir = dirname
    return 1


def set_statusbar_text(msgBar, msgtxt: str) -> None:
    """Puts msgtext into the msgBar.  Does nothing if msgBar is None"""
    if msgBar is not None:
        msgBar.config(text=msgtxt)


def indent(indentlevel=1):
    str = ""
    if indentlevel < 0:
        raise Exception("Indentlevel < 0 - you can't do that!  :)")
    while indentlevel > 0:
        str = str + "  "
        indentlevel = indentlevel - 1
    return str
