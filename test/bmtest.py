
from Tkinter import *

import Bookmark
f = Bookmark.BookmarkFactory()
f.verbose = 1
f.parseResource(open("bmarks.xml"))

win = Tk()
m = Menu()

mymenu = f.getMenu()

def fn(item):
    print "You're going to \"%s\"-vill via way of %s" % (item.getName(),
                                                         item.getURL())
    return None

m.add_cascade(label=mymenu.getName(),
              menu=mymenu.getTkMenu(m, fn))

print "Added cascade: %s" % mymenu.getName()
win.config(menu=m)
win.mainloop()

f.writeXML(open("newbm.xml", "w"), f.getMenu())
