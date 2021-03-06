#!/bin/env python3
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QFileIconProvider, QHBoxLayout, QLabel
from PyQt5.QtCore import QFileInfo, QSize, Qt

import sys
import pathlib
import magic
import subprocess
import humanfriendly
import threading
import datetime
import statusbar
from statusbar.widgets import *

# TODO: factor status bar stuff into classes
# TODO: make file handler
# TODO: make file/gui code split
# TODO: list sorting
# TODO: run file handler subprocesses and mime type retrival on seperate threads.
# This is because I/O wait might block the GUI if we do it on the GUI thread.
# Case in point: slow NFS mountpoints.
# TODO: windows support. 
# One of the few barriers for windows support is the requirement of a root 
# filesystem notation, and libmagic.

class Listing(object):
    __slots__ = ["dir", "layout", "statusbars", "widget", "newlisting", "__weakref__"]

    def __init__(self, dir, layout, statusbars):
        """ Arguments:
                :dir: pathlib.Path or String: The directory to list.
                :layout: QWidget: Any kind of container widget.

            Public Variables:
                :widget: QListWidget: The list widget we use to draw the listing.
                :layout: QWidget: The layout __init__ argument.
                :dir: pathlib.Path: The dir __init__ argument.
        """

        self.dir = pathlib.Path(dir)
        self.layout = layout
        self.statusbars = statusbars

        # Setup the widget that this Listing represents.
        self.widget = QListWidget()
        self.widget.itemActivated.connect(self.OnClick)
        self.widget.currentItemChanged.connect(self.OnSelection)
        self.widget.keyPressEvent = self.OnKey

        for child in self.dir.iterdir():
            print(f"Adding child {child}")
            item = QListWidgetItem(self.widget)
            item.setText(child.name)

        # Sometimes Qt will autofocus the first item, sometimes it won't.
        # Don't rely on this (probably undefined) behavior.
        self.widget.setCurrentRow(0)

    def OnSelection(self, item):
        print(f"onselect for {item.text()}")
        child = self.dir / item.text()

        for statusbar in self.statusbars:
            statusbar.Update(child)

    def Goto(self, dir):
        print(f"Goto: Going to {dir}")
        # This smells of a linked list.
        self.newlisting = Listing(dir, self.layout, self.statusbars)
        self.layout.replaceWidget(self.widget, self.newlisting.widget)

        # Cause the box widget to focus on the new listing.
        self.newlisting.widget.setFocus()
        self.newlisting.widget.scrollToTop()

    def Open(self, file):
        print("issa file")
        # We're a file, open it.
        # TODO: allow handling other files
        # TODO: don't run the mime type check on the GUI thread,
        # it could take a while.
        mime = magic.from_file(str(file), mime = True)
        if "audio" in mime or "video" in mime:
            subprocess.run(["mpv", str(child)])
            return
        if mime == "audio/flac":
            subprocess.run(["mpv", str(child)])
        elif mime == "application/x-executable" or mime == "application/x-pie-executable":
            subprocess.run([str(child)])
        elif mime == "application/octet-stream":
            # Sure I could have tried to execute this
            # but octet-stream tends to mean random binary
           # that isn't an executable.
            print("Issa binary file")
            return
        elif mime == "inode/x-empty":
            # This means the file is empty
            # What would we even execute this with??
            print("What's here?")
            return
        else:
            print(f"Unknown mime type! ({mime})")
            print("Trying to execute directly!")
            try:
                subprocess.run([str(child)])
            except:
                exc = sys.exc_info()
                print("Failed to execute directly")
                print(f"{exc[0]}")

    def OnClick(self, item):
        print(f"onclick for {item.text()}")

        child = self.dir / item.text()

        # We resolve the path to avoid wasting CPU time on .. directories.
        # Plus it prevents mountpoint issues.
        child = child.resolve()

        if child.is_dir():
            self.Goto(child)
        else:
            self.Open(child)

    def OnKey(self, key):
        keycode = key.key()
        # test for a specific key
        if keycode == Qt.Key_Return or keycode == Qt.Key_Right:
            curitem = self.widget.currentItem()
            self.OnClick(curitem)
        elif keycode == Qt.Key_Up:
            currow = self.widget.currentRow()
            if self.widget.item(currow - 1):
                self.widget.setCurrentRow(currow - 1)
        elif keycode == Qt.Key_Down:
            currow = self.widget.currentRow()
            if self.widget.item(currow + 1):
                self.widget.setCurrentRow(currow + 1)
            else:
                # Scroll back to top.
                self.widget.setCurrentRow(0)
        elif keycode == Qt.Key_Left:
            # We delgate directory processing to our OnClick handler.
            self.OnClick(QLabel(".."))
        else:
            print(f"key pressed: {key.text()}")

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()
header = statusbar.StatusBar([
    Text("{progname}: {progver}"), 
    Icon(20, 20),
    CurrentDirectory(),
    ])

footer = statusbar.StatusBar([
    FileSizeHuman(),
    MimeType(),
    Time("change", "%b %d %H:%M"),
])

cd = pathlib.Path(".").resolve()
listing = Listing(cd, layout, [header, footer])

layout.addLayout(header.widget)
layout.addWidget(listing.widget)
layout.addLayout(footer.widget)

window.setLayout(layout)
window.show()
app.exec_()
