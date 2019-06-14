"""
 App Name   - Jade Application Kit
 App Url    - https://codesardine.github.io/Jade-Application-Kit
 Author     - Vitor Lopes -> Copyright (c) 2016 - 2019
 Author Url - https://vitorlopes.me
"""
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox
try:
    # Testing locally
    from Utils import Instance
    from KeyBindings import KeyPressEvent
except ImportError:
    # Production
    from JAK.Utils import Instance
    from JAK.KeyBindings import KeyPressEvent

#test
from PySide2.QtWidgets import QAction, QToolBar


class JWindow(QMainWindow):

    def __init__(self, title="Jade Application Kit", icon="", transparent=False, toolbar="", parent=None):

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
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAutoFillBackground(True)

    def keyPressEvent(self, event):
        KeyPressEvent(event)

    def _icon_changed(self):
        self.setWindowIcon(self.view.icon())

    def status_message(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage(self.view.page().title(), 10000)


class JCancelConfirmDialog(QWidget):

    def __init__(self, parent, window_title, msg, on_confirm):
        """

        :param parent: Parent window or None
        :param msg: Message
        :param on_confirm: Function to execute omit parenthesis ()
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
            print("yes")
            on_confirm()
        else:
            self.destroy()


class JToolbar(QToolBar):
    def __init__(self, parent, toolbar, icon, title):
        super(JToolbar, self).__init__(parent)
        self.icon = icon
        self.setMovable(False)
        self.setIconSize(QSize(32, 32))
        self.about_title = "About"

        for button in range(len(toolbar)):
            if toolbar[button]["icon"]:
                about = QAction(QIcon.fromTheme("dialog-information"), self.about_title, self)
                item = QAction(QIcon(toolbar[button]["icon"]), toolbar[button]["name"], self)
            else:
                about = QAction("About", self)
                item = QAction(toolbar[button]["name"], self)

            item.triggered.connect(self._on_click(toolbar[button]["url"]))
            self.addAction(item)

        if not toolbar:
            about = QAction(self.about_title, self)

        about_msg = f"""
        <b>
            {title}
        </b>
        <br><br>
        <small>
             This online application is copyright and ownership of their respective authors.
             <br>
             The wrapper offers the ability to run it, as a self contained desktop application.
        </small>
        <br>
        <center>
           <br>
             Toggle Full Screen    [  F11  ] 
           <br><br>
             Zoom In    [  CTRL +  ] 
           <br><br>
             Zoom Out    [  CTRL -  ] 
           <br><br><br>
           <b>
              Powered by:
           </b> 
           <a href='https://github.com/codesardine/Jade-Application-Kit'>Jade Application Kit</a><center>
           Native Hybrid Apps on Linux.
           <br>
           <small>
               <b>
                   Using QT WebEngine
               <b>
           </small>
           <br>
           <small>
               <br>
                   JAK: Comes with absolutely no warranty. License: GPL
               <br>
               <b>
                   JAK: Author: Vitor Lopes
               <b>
           </small>
        </center>        
        """

        about.triggered.connect(self._on_click(about_msg, self.about_title))
        self.addAction(about)

    def _on_click(self, url: str, title=""):
        """
        :return: function
        """
        view = Instance.retrieve("view")
        if url.startswith("https"):
            return lambda: view.setUrl(url)
        else:
            msg = url
            return lambda: InfoDialog(self, title, msg)


class InfoDialog(QWidget):

    def __init__(self, parent, title, msg):
        """

        :param parent: Parent window or None
        :param msg: Message
        :param on_confirm: Function to execute omit parenthesis ()
        """
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        QMessageBox.information(parent, title, msg, QMessageBox.Ok)
        self.show()
