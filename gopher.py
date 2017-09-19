# gopher.py
# $Id: gopher.py,v 1.7 2001/07/11 22:43:09 s2mdalle Exp $
# Gopher protocol definitions.
# Written by David Allen <mda@idatar.com>
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
RESPONSE_FILE    = '0' # Item is a file
RESPONSE_DIR     = '1' # Item is a directory
RESPONSE_CSO     = '2' # Item is a CSO phone-book server
RESPONSE_ERR     = '3' # Error
RESPONSE_BINHEX  = '4' # Item is a BinHexed Macintosh file.
RESPONSE_DOSBIN  = '5' # Item is DOS binary archive of some sort.
RESPONSE_UUE     = '6' # Item is a UNIX uuencoded file.
RESPONSE_INDEXS  = '7' # Item is an Index-Search server.
RESPONSE_TELNET  = '8' # Item points to a text-based telnet session.
RESPONSE_BINFILE = '9' # Item is a binary file!
RESPONSE_REDSERV = '+' # Item is a redundant server
RESPONSE_TN3270  = 'T' # Item points to a text-based tn3270 session.
RESPONSE_GIF     = 'g' # Item is a GIF format graphics file.
RESPONSE_IMAGE   = 'I' # Item is some kind of image file.
RESPONSE_UNKNOWN = '?' # Unknown.  WTF?
RESPONSE_BITMAP  = ':' # Gopher+ Bitmap response
RESPONSE_MOVIE   = ";" # Gopher+ Movie response
RESPONSE_SOUND   = "<" # Gopher+ Sound response

# The following are types not found in the RFC definition of gopher but that
# I've encountered on the net, so I added
RESPONSE_BLURB   = 'i'
RESPONSE_HTML    = 'h'

# Gopher+ errors
ERROR_NA         = '1' # Item is not available.
ERROR_TA         = '2' # Try again later (eg. My load is too high right now.)
ERROR_MOVED      = '3' # Item has moved.

responses = { "%s" % RESPONSE_FILE    : "File:",
              "%s" % RESPONSE_DIR     : "Directory:",
              "%s" % RESPONSE_CSO     : "CSO phone-book server:",
              "%s" % RESPONSE_ERR     : "Error:",
              "%s" % RESPONSE_BINHEX  : "BinHexed Macintosh file:",
              "%s" % RESPONSE_DOSBIN  : "DOS binary archive:",
              "%s" % RESPONSE_UUE     : "UNIX UUEncoded file:",
              "%s" % RESPONSE_INDEXS  : "Index-Search server:",
              "%s" % RESPONSE_TELNET  : "Telnet session:",
              "%s" % RESPONSE_BINFILE : "Binary file:",
              "%s" % RESPONSE_REDSERV : "Redundant server:",
              "%s" % RESPONSE_TN3270  : "tn3270 session:",
              "%s" % RESPONSE_GIF     : "GIF file:",
              "%s" % RESPONSE_IMAGE   : "Image file:",
              "%s" % RESPONSE_BLURB   : " ",
              "%s" % RESPONSE_HTML    : "HTML file:",
              "%s" % RESPONSE_BITMAP  : "Bitmap Image:",
              "%s" % RESPONSE_MOVIE   : "Movie:",
              "%s" % RESPONSE_SOUND   : "Sound:",
              "%s" % RESPONSE_UNKNOWN : "Unknown:" }
errors    = { "%s" % ERROR_NA         : "Error: Item is not available.",
              "%s" % ERROR_TA         : "Error: Try again (server busy)",
              "%s" % ERROR_MOVED      : "Error: This resource has moved." }

# There is nothing special about these numbers, just make sure they're
# all unique.
QUESTION_ASK       = 20
QUESTION_ASKP      = 21
QUESTION_ASKL      = 22
QUESTION_ASKF      = 23
QUESTION_SELECT    = 24
QUESTION_CHOOSE    = 25
QUESTION_CHOOSEF   = 26
QUESTION_NOTE      = 27

# Mapping from Gopher+ types to internal values.
questions = { "Ask"             : QUESTION_ASK,
              "AskP"            : QUESTION_ASKP,
              "AskL"            : QUESTION_ASKL,
              "AskF"            : QUESTION_ASKF,
              "Select"          : QUESTION_SELECT,
              "Choose"          : QUESTION_CHOOSE,
              "ChooseF"         : QUESTION_CHOOSEF,
              "Note"            : QUESTION_NOTE }

questions_types = { "%s" % QUESTION_ASK          : "Ask",
                    "%s" % QUESTION_ASKP         : "AskP",
                    "%s" % QUESTION_ASKL         : "AskL",
                    "%s" % QUESTION_ASKF         : "AskF",
                    "%s" % QUESTION_SELECT       : "Select",
                    "%s" % QUESTION_CHOOSE       : "Choose",
                    "%s" % QUESTION_CHOOSEF      : "ChooseF" }

# Colors - not related to gopher protocol functioning, but useful.
RED         = "#FF0000"
GREEN       = "#00FF00"
BLUE        = "#0000FF"
WHITE       = "#FFFFFF"
BLACK       = "#000000"
