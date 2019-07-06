#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

from PySide2.QtCore import Qt, QSize, QSettings
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox, QDesktopWidget
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
        self.title = title
        self.video_corner = False
        self.center = QDesktopWidget().availableGeometry().center()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        self.toolbar = JToolbar(self, toolbar, icon, title)
        self.addToolBar(self.toolbar)
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

    def hide_show_bar(self):
        if self.isFullScreen() or self.video_corner:
            self.statusbar.hide()
            self.toolbar.hide()
        else:
            self.statusbar.show()
            self.toolbar.show()

    def get_geometry(self):
        return QDesktopWidget().availableGeometry(self)

    def default_size(self, size: str):
        # Set to 70% screen size
        if size is "width":
            return self.get_geometry().width() * 2 / 3
        elif size is "height":
            return self.get_geometry().height() * 2 / 3

    def set_window_to_defaults(self):
        self.window_original_position.moveCenter(self.center)
        self.move(self.window_original_position.topLeft())
        self.resize(self.default_size("width"), self.default_size("height"))
        self.hide_show_bar()
        self.setWindowFlags(Qt.Window)
        self.show()

    def set_window_to_corner(self):
        self.move(self.window_original_position.bottomRight())
        # Set to 30% screen size
        self.resize(self.get_geometry().width() * 0.7 / 2, self.get_geometry().height() * 0.7 / 2)
        self.hide_show_bar()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()

    def corner_window(self):
        if self.video_corner:
            self.video_corner = False
            self.set_window_to_defaults()
        else:
            self.video_corner = True
            if self.isFullScreen():
                self.showNormal()
            self.set_window_to_corner()


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
           <br><b>
             F11 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Toggle Full Screen 
           <br>
             F12 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Toggle Corner Window
           <br>
             CTRL + &nbsp; &nbsp; Zoom In  
           <br>
             CTRL - &nbsp; &nbsp;  Zoom Out  
           <br><br></b>
           <center>
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
