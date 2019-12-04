import toml
import filetype
import subprocess
import timeit
import re
import functools
import collections
import os
import importlib

""" assoc.py
    assoc.py handles the mapping of handler programs to mime types.
    We use our own TOML "database" here, but it's trivial to implement
    a database class for the XDG standard.
"""

class NoAssociationException(Exception):
    pass

class MagicMimeTypeDB():
    def __init__(self):
        self.magic = importlib.import_module("magic")

    def Lookup(self, file):
        return magic.from_file(file, mime = True)

class FileTypeMimeTypeDB():
    def __init__(self):
        self.filetype = importlib.import_module("filetype")

    def Lookup(self, file):
        type = self.filetype.guess(file)
        if type:
            return type.mime

class MimeTypeDB():
    """ MimeTypeDB is a wrapper against the various ways of finding mimetypes.
    """

    def __init__(self, methods):
        self.methods = methods

    def Lookup(self, file):
        for method in self.methods:
            mime = method.Lookup(file)
            if mime:
                return mime

        # If we can't find the mimetype return it as an octet-stream.
        # Octet stream is another way of saying "random binary data".
        return "application/octet-stream"

class AssocDB():
    """ AssocDB is a reference implementation of an Associations Database.
        It uses a TOML file for the database and supports globbing. """

    def __init__(self, dbfile):
        with open(dbfile, "r") as file:
            tomldata = toml.load(file, _dict = collections.OrderedDict)
            self.assocs = tomldata["associations"]

    @functools.lru_cache(maxsize = None)
    def Lookup(self, mimetype):
        # While this /can/ be handled by regular expressions, It's better not to.
        # Dictonary lookups are a lot quicker than compiling a bunch of regexs
        # in a loop.
        try:
            return self.assocs[mimetype]
        except KeyError:
            pass

        # Perform regexes for more complex associations.
        # This takes O(n) time vs the O(1) time of the dict lookup.
        # It also takes longer with the more associations one has.
        for assoc in self.assocs:
            regex = re.compile(assoc)
            if regex.match(mimetype):
                return self.assocs[assoc]

        # There are no entrys,
        # the only thing we can do now is raise an exception.
        raise NoAssociationException()

    def LookupFromFile(self, file):
        # I've decided against using a LRU cache for this function.
        # Thinking about it, how many people are going to be opening the same
        # file multible times per instance?
        # It's a waste of memory. My interests are better spent
        # optimizing the Lookup function and caching it.
        # The same mime type will be looked up multible times per instance,
        # It's actually the heaviest function in this entire ordeal.

        m = MimeTypeDB([FileTypeMimeTypeDB(), MagicMimeTypeDB()])
        print(m.Lookup(file))
        assoc = self.Lookup(m.Lookup(file))
        return assoc

class Runner():
    __slots__ = ["assocdb"]

    def __init__(self, assocdb):
        self.assocdb = assocdb

    def Run(self, file, foreground = False):
        assoc = self.assocdb.LookupFromFile(file)

        # Format the assoc.
        assoc = assoc.format(
                file = file
        )

        print(f"Running {file} with {assoc}")

        proc = subprocess.Popen(assoc, shell = True)
        if foreground:
            proc.wait()
if __name__ == "__main__":
    # Load the database.
    db = AssocDB("assoc.toml")

    # Load the Runner.
    r = Runner(db)

    # Guess mimetype.
    r.Run("test.flac", foreground = True)

    for dirpath, dirnames, filenames in os.walk("/"):
        for filename in filenames:
            print(f"Lookup: {db.Lookup.cache_info()}")
            try:
                db.LookupFromFile(f"{dirpath}/{filename}")
            except NoAssociationException:
                pass
            except:
                pass

    print("Done!")
    while True:
        pass
