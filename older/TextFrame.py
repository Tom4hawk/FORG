#!env python
# Written by David Allen <s2mdalle@titan.vcu.edu>
# http://opop.nols.com/
# Released under the terms of the GNU General Public License
########################################################################
from gtk import *

class TextFrame(GtkTable):
    def __init__(self, data):
        GtkTable.__init__(self, rows=3, cols=2, homogeneous=FALSE)
        self.popupMenu      = self.makePopupMenu()
        self.data           = data
        self.text           = GtkText()
        self.text.set_editable(FALSE)
        self.text.set_word_wrap(FALSE)
        self.text.set_line_wrap(FALSE)
        self.attach(self.text, 0, 1, 0, 1,
                    xoptions=EXPAND|FILL, yoptions=EXPAND|FILL,
                    ypadding=0, xpadding=0)
        self.vscroll = GtkVScrollbar(self.text.get_vadjustment())
        self.attach(self.vscroll, 1, 2, 0, 1,
                    xoptions=FILL, yoptions=FILL,
                    ypadding=0, xpadding=0)
        self.hscroll = GtkHScrollbar(self.text.get_hadjustment())
        self.attach(self.hscroll, 0, 1, 1, 2,
                    xoptions=FILL, yoptions=FILL,
                    ypadding=0, xpadding=0)
        self.messageBox = GtkVBox(0, 0)
        self.attach(self.messageBox, 0, 2, 2, 3,
                    xoptions=FILL, yoptions=FILL,
                    ypadding=0, xpadding=0)
        self.connect('button_press_event', self.contextPopup)
        self.loadData()
        self.show_all()
        return None

    def saveDialog(self, *args):
        fs = GtkFileSelection()
        fs.ok_button.connect('clicked', self.saveToFile, fs)
        fs.cancel_button.connect('clicked', lambda *args: args[2].destroy())
        fs.show_all()
        
    def makePopupMenu(self):
        pmenu    = GtkMenu()
        save     = GtkMenuItem(label="Save")
        close    = GtkMenuItem(label="Close")

        save.connect('activate', self.saveDialog)
        close.connect('activate', self.destroy)
        pmenu.append(save)
        pmenu.append(close)
        return pmenu

    def saveToFile(self, emitter, fs, *stuff):
        filename = fs.get_filename()
        fs.destroy()
        
        try:
            fp = open(filename, "w")
        except:
            print "Error opening file"
            return None
        
        ln = self.text.get_length()
        pt = 0

        while pt < ln:
            endpoint = pt + 1024
            if endpoint > ln:
                endpoint = ln
            try:
                fp.write(self.text.get_chars(pt, endpoint))
            except IOError, errstr:
                print "Error writing data to file: %s" % errstr
                return None
            pt = pt + 1024
        fp.flush()
        fp.close()
        return 1

    def contextPopup(self, emitter, event):
        if event.button == 3:
            self.popupMenu.popup(None, None, None, event.button, event.time)
            self.popupMenu.show_all()
        return None

    def loadData(self):
        self.insert(None, None, None, self.data)
    
    def test(self, *args):
        self.notify("This is a test")
        self.notify("This is another test")
        self.notify("This is yet another test")
    
    # Bunch of crap text methods.  This is the downside of extending
    # GtkTable instead of GtkText which is the meat of the widget. :)
    def backward_delete(self, nchars):
        return self.text.backward_delete(nchars)
    def freeze(self, obj=None):
        return self.text.freeze(obj)
    def get_hadjustment(self):
        return self.text.get_hadjustment()
    def get_length(self):
        return self.text.get_length()
    def get_point(self):
        return self.text.get_point()
    def get_vadjustment(self):
        return self.text.get_vadjustment()
    def insert(font, fg, bg, string):
        return self.text.insert(font, fg, bg, string)
    def insert_defaults(self, chars):
        return self.text.insert_defaults(chars)
    def set_adjustments(self, hadj, vadj):
        return self.text.set_adjustments(hadj, vadj)
    def set_editable(self, editable):
        return self.text.set_editable(editable)
    def set_line_wrap(self, line_wrap):
        return self.text.set_line_wrap(line_wrap)
    def thaw(self, obj=None):
        return self.text.thaw(obj)
    def set_point(self, point):
        return self.text.set_point(point)
    def forward_delete(self, length):
        return self.text.forward_delete(length)
    def set_word_wrap(self, word_wrap):
        return self.text.set_word_wrap(word_wrap)
    def insert(self, o, t, th, text):
        return self.text.insert(o, t, th, text)
    def changed(self):
        return self.text.changed()
    def claim_selection(self, claim, time):
        return self.text.claim_selection(claim, time)
    def copy_clipboard(self):
        return self.text.copy_clipboard()
    def cut_clipboard(self):
        return self.text.cut_clipboard()
    def delete_selection(self):
        return self.text.delete_selection()
    def delete_text(self, start, end):
        return self.text.delete_text(self, start, end)
    def get_chars(self, start, end):
        return self.text.get_chars(start, end)
    def get_position(self):
        return self.text.get_position()
    def insert_text(self, new_text):
        return self.text.insert_text(new_text)
    def paste_clipboard(self):
        return self.text.paste_clipboard()
    def select_region(self, start, end):
        return self.text.select_region(start, end)
    def set_editable(self, is_editable):
        return self.text.set_editable(is_editable)
    def set_position(self, pos):
        return self.text.set_position(pos)
