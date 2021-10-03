# Copyright (C) 2021 Tom4hawk
#
# Contains many different program dialogs used for information and data
# entry purposes.
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
import tkinter as tk
from functools import partial


class Dialog:
    def __init__(self, title, buttons, parent=None, command=None, default_button=None):
        self.__frame_content = None
        self.__window = None
        self.dialog(title, buttons, parent, command, default_button)

    def dialog(self, title, buttons, parent=None, command=None, default_button=None):
        dialog_window = tk.Toplevel(parent)
        dialog_window.title(title)

        # Frame used to pack elements provided by caller in the later stage
        content_frame = tk.Frame(dialog_window)
        content_frame.pack(anchor=tk.N, fill=tk.X)

        # Buttons
        button_frame = tk.Frame(dialog_window)

        for idx, button in enumerate(buttons):
            active = tk.ACTIVE if button == default_button else tk.NORMAL
            btn = tk.Button(button_frame, text=button, state=active, command=partial(command, button))
            btn.grid(column=idx, row=0, padx=4, pady=4)
            button_frame.columnconfigure(idx, weight=1)

        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.__frame_content = content_frame
        self.__window = dialog_window

    def interior(self):
        return self.__frame_content

    def window(self):
        return self.__window

    def destroy(self):
        if self.__window:
            self.__window.destroy()
        self.__frame_content = None
        self.__window = None
