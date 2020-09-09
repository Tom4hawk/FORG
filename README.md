Forg
===
The FORG is a __Linux__ graphical client for [Gopher](https://en.wikipedia.org/wiki/Gopher_\(protocol\)) written in Python. It will let you browse the world-wide gopherspace and handles various types of media, including HTML and video.

Table of contents
=================
* [Features](#features)
* [Requirements](#requirements)
	* [Python & Libraries](#python--libraries)
	* [Windows/MacOSX support](#windowsmacosx-support)
* [How to use](#how-to-use)
	* [Basics](#basics)
    * [Associate extensions](#associate-extensions)
    * [Bookmarks](#bookmarks)
* [Original author](#original-author)
* [Why fork](#why-fork)
* [To do](#to-do)
* [License](#license)



Features
========
- Ability to load other programs with different file formats. I.e. this program does not interpret HTML, so you may want to associate .html files with [Firefox](https://firefox.com/), so it will be launched upon saving a .html file
- Full caching of directories and files
- Searching support.  (Tested against gopher.floodgap.com's Veronica, but of course)
- Bookmarking support.  Bookmarks are written in XBEL and support arbitrary folders and subfolders
- Bookmark editing, similar to Firefox
- Directories are searchable by name
- Statistics on size of cache, number of files in the cache, and number of documents in the queue
- Ability to save files and directories.  (Note: when directories are saved, the protocol information that the server sent is what is saved to disk...for now)
- ASK menus - users can interact with programs on foreign servers through the use of miniature questionnaires
- Right click context menus on all items providing all available information on a resource.  (If the server supports Gopher+)
- Between 0 and 100% complete implementation of Gopher *AND* Gopher+!!! :)
- Managerspeak.  This program leverages automatic internet data retrieval and storaging technologies for quasi-reliable interlocked handshake protocol interaction, allowing open-ended failsafe solutions to be developed in the realm of...oh whatever

Requirements
============
Python & Libraries
------------------
You will need 4 things. Python 3.4 or newer, Tkinter (should be bundled with Python), Pmw and Pillow. There is a good chance that your distribution has all of them in official repository. You can use _pip_ if you cannot/don't want to use official repository.

Windows/MacOSX support
----------------------
Theoretically, this program should run under these systems. I've never tested this theory and I'm not going to.

How to use
==========
Basics
------
To run the program, run:

    ./forg.py host
as an example, host can be "___gopher.floodgap.com___", "___gopher.meulie.net___" or "___gopher.quux.org___", which are all valid gopher sites.  
Alternatively, you can use URL syntax, as in:

    ./forg gopher://gopher.quux.org

Associate extensions
--------------------
How to Associate extensions

Bookmarks
---------
How to bookmarks

Original author
===============
_David Allen_ <mda@idatar.com>  
__http://opop.nols.com/__  
The upstream home page mentioned in original README is unavailable but if you are curious there is a copy of the site on [archve.org](http://web.archive.org/web/20030416195623/http://opop.nols.com/forg.shtml)

Why fork
========
Original program is no longer maintained (latest release is from 2001) and doesn't work well with newer Pythons (quote from original readme: "The version of python required is 1.5.2, (...) Python version 2.0 is strongly suggested."). This fork aims to address those two problems.

To do
=====
- [x] Port to newest Python 2.x
- [x] Port to Python 3.x
	- [x] Remove dependency on _xmllib_
- [ ] Change name
- [ ] Stop using [PMW](http://pmw.sourceforge.net/) (library doesn't look alive)
- [ ] Scrolling with mouse wheel
- [ ] Start using _[flake8](http://flake8.pycqa.org/)_
- [ ] Add Gemini protocol support
- [ ] Gtk Gui
- [ ] Ncurses Gui
- [ ] QT Gui
- [ ] Mobile version for Phosh
- [ ] Mobile version for UBPorts
- [ ] Mobile version for Plasma Mobile
- [ ] AppImage package
- [x] Support for XDG Base Directory Specification
- [ ] Clean directory structure 

License
=======
[GNU General Public License, version 2](https://www.gnu.org/licenses/gpl-2.0.html) - copy of the licence is in _COPYING_ file
