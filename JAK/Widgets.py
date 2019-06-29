#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox
from JAK.Utils import Instance
from JAK.KeyBindings import KeyPress
from PySide2.QtWidgets import QAction, QToolBar


class JWindow(QMainWindow):
    """ #### Imports: from JAK.Widgets import JWindow """
    def __init__(self, title="Jade Application Kit", icon="", transparent=False, toolbar="", parent=None):
        """
        * :param title:str
        * :param icon:str
        * :param transparent:bool
        * :param toolbar:dict
        * :param parent: Parent widget
        """

        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        self.bar = JToolbar(self, toolbar, icon, title)
        self.addToolBar(self.bar)
        #self.addToolBar(Qt.RightToolBarArea, self.bar)

        view = Instance.retrieve("view")
        if view:
            self.view = view
            self.setCentralWidget(self.view)
            self.view.page().titleChanged.connect(self.status_message)

        if icon:
            self.setWindowIcon(QIcon(icon))
        else:
            if view:
                self.view.iconChanged.connect(self._icon_changed)

        if transparent:
            # Set Background Transparency
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAutoFillBackground(True)

    def keyPressEvent(self, event):
        KeyPress(event)

    def _icon_changed(self):
        self.setWindowIcon(self.view.icon())

    def status_message(self):
        # Show status message
        self.statusbar = self.statusBar()
        self.statusbar.showMessage(self.view.page().title(), 10000)


class JCancelConfirmDialog(QWidget):
    """ #### Imports: from JAK.Widgets import JCancelConfirmDialog """
    def __init__(self, parent, window_title, msg, on_confirm):
        """
        * :param parent: Parent window
        * :param window_title:str
        * :param msg:str
        * :param on_confirm: Function to execute omit parenthesis ()
        """
        super().__init__()
        reply = QMessageBox.question(parent, window_title, msg, QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(window_title)
        view = Instance.retrieve("view")
        if view:
            self.setWindowIcon(view.icon())
        self.show()

        if reply == QMessageBox.Yes:
            on_confirm()
        else:
            self.destroy()


class JToolbar(QToolBar):
    """ #### Imports: from JAK.Widgets import JToolbar """
    def __init__(self, parent, toolbar, icon, title):
        """
        * :param parent: Parent window
        * :param toolbar:dict
        * :param icon:str
        * :param title:str
        """
        super(JToolbar, self).__init__(parent)
        self.icon = icon
        self.setMovable(False)
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setIconSize(QSize(32, 32))
        self.about_title = "About"

        if toolbar:
            # If a dict is passed generate buttons from dict
            for btn in toolbar:
                try:
                    if btn["icon"]:
                        about = QAction(QIcon.fromTheme("dialog-information"), self.about_title, self)
                        item = QAction(QIcon(btn["icon"]), btn["name"], self)
                except KeyError:
                    about = QAction("About", self)
                    item = QAction(btn["name"], self)

                item.triggered.connect(self._on_click(btn["url"]))
                self.addAction(item)
        else:
            about = QAction(self.about_title, self)

        about_msg = f"""
        <body style='margin-right:68px;color:#454545;'><b>
            {title}
        </b>
        <br><br>
        <small>
             This online application is copyright and ownership of their respective authors.
             <br><br>
             This wrapper offers the ability to run web applications, as a self contained native desktop application.
              Enjoy.
        </small>
        <br>
        <center>
           <br><b>
             Toggle Full Screen    [  F11  ] 
           <br><br>
             Zoom In    [  CTRL +  ] 
           <br><br>
             Zoom Out    [  CTRL -  ] 
           <br><br><br></b>
           <b><small>
              Powered by:
           </b></small>
           <a href='https://github.com/codesardine/Jade-Application-Kit'>Jade Application Kit</a><center>
           <small>
           Native Hybrid Apps on Linux.
           <br>
               <b>
                   Using QT WebEngine
               <b>
           </small>
           <br>
           <small>
               <br>
                   This application comes with no warranty. License: <b>GPL</b>
               <br>
                   Author:<b>Vitor Lopes<b>
           </small>
        </center>
        </body> 
        """

        about.triggered.connect(self._on_click(about_msg, self.about_title))
        self.addAction(about)

    def _on_click(self, url: str, title=""):
        view = Instance.retrieve("view")
        if url.startswith("https"):
            return lambda: view.setUrl(url)
        else:
            msg = url
            return lambda: InfoDialog(self, title, msg)


class InfoDialog(QWidget):
    """ #### Imports: from JAK.Widgets import InfoDialog """
    def __init__(self, parent, title, msg):
        """
        * :param parent: Parent window
        * :param msg:str
        * :param on_confirm: Function to execute omit parenthesis ()
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        QMessageBox.information(parent, title, msg, QMessageBox.Ok)
        self.show()
