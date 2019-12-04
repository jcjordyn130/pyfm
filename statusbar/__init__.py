from PyQt5.QtWidgets import QHBoxLayout

class StatusBar():
    """ Arguments:
            :items: List: A list of status bar items.

        Variables:
            :widget: QLayout: A layout widget we add the items to.
    """

    def __init__(self, items):
        self.items = items
        self.widget = QHBoxLayout()

    def Update(self, file):
        """ Update() updates all of the items in a status bar with a new file.
            Arguments:
                :file: pathlib.Path: The file to use for the widgets.
        """

        for item in self.items:
            print(f"Updating status bar item {item}")

            # The reason we do this item at a time is to prevent race issues
            # when updating multible widgets.
            try:
                item.widget.setParent(None)
            except AttributeError:
                # This only fails if `item.widget` doesn't exist
                # That only happens if we haven't initialized it yet.
                pass

            item.Update(file)
            self.widget.addWidget(item.widget)
