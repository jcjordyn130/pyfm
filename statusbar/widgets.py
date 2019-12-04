from PyQt5.QtWidgets import QLabel, QFileIconProvider
from PyQt5.QtCore import QFileInfo, QSize, Qt
import humanfriendly
import magic
import sys
import datetime

class Icon():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Update(self, file):
        # TODO: wtf is this?
        iconprovider = QFileIconProvider()

        fileinfo = QFileInfo(str(file))

        icon = iconprovider.icon(fileinfo)
        iconsize = QSize(self.x, self.y)

        self.widget = QLabel()
        self.widget.setPixmap(icon.pixmap(iconsize))

class FileSizeHuman():
    def __init__(self):
        # TODO: allow changing to MiB/MB.
        pass

    def Update(self, file):
        stat = file.stat()
        print(f"stat call on {file}: {stat}")
        size = humanfriendly.format_size(stat.st_size)
        self.widget = QLabel(size)

class MimeType():
    def Update(self, file):
        try:
            mime = magic.from_file(str(file), mime = True)
        except IsADirectoryError:
            # It seems libmagic doesn't provide this for us.
            mime = "inode/directory"
        except:
            # TODO: proper error handling of status bar objects.
            exc = sys.exc_info()
            mime = f"exception/{exc[0].__name__}"

        self.widget = QLabel(mime)

class Text():
    formatters = {
            "progver": "0.0.1",
            "progname": "PyFM"
    }

    def __init__(self, text):
        self.text = text

    def Update(self, file):
        formattedtext = self.text.format(**self.formatters)
        self.widget = QLabel(formattedtext)

class CurrentDirectory():
    def Update(self, file):
        # The way we get the current directory is by looking at the parent
        # of the current selection.
        self.widget = QLabel(str(file.parent))

class Time():
    def __init__(self, type, format):
        self.format = format
        self.type = type
        if not type in ["access", "change"]:
            # TODO: special exception needed.
            raise Exception(f"Invalid time type {type}")

    def Update(self, file):
        stat = file.stat()
        if self.type == "access":
            time = datetime.datetime.fromtimestamp(stat.st_atime)
            formattedtime = time.strftime(self.format)
            self.widget = QLabel(str(formattedtime))
        elif self.type == "change":
            time = datetime.datetime.fromtimestamp(stat.st_mtime)
            formattedtime = time.strftime(self.format)
            self.widget = QLabel(str(formattedtime))
