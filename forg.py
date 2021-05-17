#!/usr/bin/python3
# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020-2021 Tom4hawk
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
##############################################################################

import sys
from TkGui import *


def main(item):
    try:
        app = TkGui(item)
        app.mainloop()
    except KeyboardInterrupt:
        app.quit()
        exit()


print("Starting the FORG")
url = ""

try:
    url = sys.argv[1]
    if (url[:]).lower().find("gopher://") == -1:
        url = "gopher://" + url
except:
    url = None

# Start the program
print("Starting program with \"%s\"" % url)
main(url)
