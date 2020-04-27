#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

from JAK.Utils import  bindings
if bindings() == "PyQt5":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWidgets import QDockWidget
else:
    from PySide2.QtCore import Qt
    from PySide2.QtWebEngineWidgets import QWebEngineView
    from PySide2.QtWidgets import QDockWidget


class WebView(QWebEngineView):

    def __init__(self, parent=None):
        QWebEngineView.__init__(self, parent)

    def set_inspected_view(self, view=None):
        self.page().setInspectedPage(view.page() if view else None)


class InspectorDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        title = "Inspector"
        self.setWindowTitle(title)
        self.setObjectName(title)
