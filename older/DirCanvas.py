# DirCanvas.py
# Written by David Allen <s2mdalle@titan.vcu.edu>
# Takes a GopherResource and a GopherResponse object and turns it into
# a canvas object that displays the contents of the directory on screen.
#
# This is acting a bit strange to say the least, so for now, we stick with the
# other method.
###########################################################################

import gopher
from GopherResponse import *
from Tkinter import *
import Pmw

class DirCanvas:
    DirCanvasException = "You can't do that to me, that's filthy!"

    def __init__(self, parent, resource, response):
        self.canvas = Pmw.ScrolledCanvas(parent,
                                         vscrollmode='dynamic',
                                         hscrollmode='dynamic')
        self.pack = self.canvas.pack
        self.resource  = resource
        self.response  = response
        self.baselinex = 50
        self.baseliney = 50

        resps = self.response.getResponses()

        for x in range(0, len(resps)):
            r = resps[x]
            basex = self.baselinex
            basey = self.baseliney * x

            if r.getTypeCode() == RESPONSE_BLURB:
                self.canvas.create_text(basex, basey, text=r.getName())
            else:
                self.canvas.create_text(basex, basey, text=r.getType())
                basex = basex + 100
                self.canvas.create_text(basex, basey, text=r.getName())
        return None

