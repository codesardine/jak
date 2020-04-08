#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

import sys
import os
from JAK.Utils import Instance, bindings
from JAK.KeyBindings import KeyPress
if bindings() == "PyQt5":
    from PyQt5.QtCore import Qt, QSize, QUrl
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QDesktopWidget, QSystemTrayIcon, QDockWidget,\
        QAction, QToolBar, QMenu, QMenuBar, QFileDialog
else:
    from PySide2.QtCore import Qt, QSize, QUrl
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox, QDesktopWidget, QSystemTrayIcon, QDockWidget,\
        QAction, QToolBar, QMenu, QMenuBar, QFileDialog


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, app, title):
        self.title = title
        self.icon = icon
        super(SystemTrayIcon, self).__init__(icon, parent=app)
        self.setContextMenu(self.tray_menu())
        self.show()

    def tray_menu(self):
        """
        Create menu for the tray icon
        """
        self.quit = QAction(f"&Quit {self.title}", self)
        self.quit.triggered.connect(sys.exit)
        self.menu = QMenu()
        self.menu.addAction(self.quit)
        return self.menu


class JWindow(QMainWindow):
    """ #### Imports: from JAK.Widgets import JWindow """
    def __init__(self, config):
        """
        * :param title:str
        * :param icon:str
        * :param transparent:bool
        * :param toolbar:dict
        * :param parent: Parent widget
        """

        QMainWindow.__init__(self)
        self.config = config
        self.video_corner = False
        self.center = QDesktopWidget().availableGeometry().center()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(config["title"])
        if config["icon"] and os.path.isfile(config["icon"]):
            self.icon = QIcon(config["icon"])
        else:
            # TODO detect active icon theme
            QIcon.setThemeName("Papirus-Maia")
            icon_paths = QIcon.themeSearchPaths()
            icon_paths.append("/usr/share/pixmaps")
            QIcon.setThemeSearchPaths(icon_paths)
            self.icon = QIcon.fromTheme("applications-internet")

        view = Instance.retrieve("view")
        if view:
            self.view = view
            self.setCentralWidget(self.view)
            self.view.iconChanged.connect(self._icon_changed)
            if config["online"]:
                self.view.page().titleChanged.connect(self.status_message)

        if config["transparent"]:
            # Set Background Transparency
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAutoFillBackground(True)

        if config["online"]:
            # Do not display toolbar or system tray offline
            if config["toolbar"]:
                self.toolbar = JToolbar(self, config["toolbar"], self.icon, config["title"])
                self.addToolBar(self.toolbar)
            self.system_tray = SystemTrayIcon(self.icon, self, config["title"])
            self._set_icons()
            self.setMenuBar(Menu(self, config["menus"]))

        if config["debug"]:
            dock = Inspector("Dev Tools", self)
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)
            from JAK.WebEngine import JWebView
            config["web_contents"] = "http://127.0.0.1:9000"
            inspector_view = JWebView(config)
            dock.setWidget(inspector_view)

    def keyPressEvent(self, event):
        KeyPress(event)

    def _set_icons(self):
        self.setWindowIcon(self.icon)
        if self.config["online"]:
            self.system_tray.setIcon(self.icon)

    def _icon_changed(self):
        if not self.view.icon().isNull():
            self.icon = self.view.icon()
            self._set_icons()

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
        if size == "width":
            return self.get_geometry().width() * 2 / 3
        elif size == "height":
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
    def __init__(self, parent, title, msg, on_confirm):
        """
        * :param parent: Parent window
        * :param window_title:str
        * :param msg:str
        * :param on_confirm: Function to execute use parenthesis ()
        """
        super().__init__(parent)
        reply = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        view = Instance.retrieve("view")
        if view:
            self.setWindowIcon(view.icon())
        if reply == QMessageBox.Yes:
            on_confirm()
        else:
            self.destroy()
        self.show()


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
                        item = QAction(QIcon(btn["icon"]), btn["name"], self)
                except KeyError:
                    item = QAction(btn["name"], self)

                item.triggered.connect(self._on_click(btn["url"]))
                self.addAction(item)

    def _on_click(self, url: str, title=""):
        view = Instance.retrieve("view")
        if url.startswith("https"):
            return lambda: view.setUrl(QUrl(url))
        else:
            msg = url
            return lambda: InfoDialog(self, title, msg)


class Menu(QMenuBar):

    def __init__(self, parent, menus):

        super(Menu, self).__init__(parent)
        if menus:
            for menu in menus:
                if type(menu) is dict:
                    title = self.addMenu(menu["title"])
                    for entry in menu["entries"]:
                        submenu = QAction(entry[0], self)
                        title.addAction(submenu)
                        print(entry[1])
                        submenu.triggered.connect(self._on_click(entry[1]))

        help_menu = {"title": "Keyboard Shortcuts", "text": """
                <body style='margin-right:46px;'><b>
                    F11 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Toggle Full Screen 
                <br>
                    F12 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Toggle Corner Window
                <br>
                    CTRL + &nbsp; &nbsp; Zoom In  
                <br>
                    CTRL - &nbsp; &nbsp;  Zoom Out  
                </body>
        """},\
        {"title": "About JAK", "text": """
                <body style='margin-right:46px;'>
                <small>
                    This online application is copyright and ownership of their respective authors.
                    <br><br>
                    This wrapper offers the ability to run web applications, as a self contained native desktop application.
                    Enjoy.
                </small>
                <br>
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
        """}

        help = self.addMenu("Help")
        for entry in help_menu:
            submenu = QAction(entry["title"], self)
            submenu.triggered.connect(self._on_click(entry["text"], entry["title"]))
            help.addAction(submenu)

    def _on_click(self, url: str, title=""):
        if url.startswith("https"):
            view = Instance.retrieve("view")
            return lambda: view.setUrl(QUrl(url))

        elif url.endswith("()"):
            from JAK import IPC
            return lambda: IPC.Communication.activate(url)
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


class FileChooserDialog(QWidget):

    def __init__(self, parent=None, file_type="", title="Choose a File"):
        super().__init__(parent)
        self.file_type = file_type
        self.title = title
        self.show()
                    
    def choose_file(self):
        dialog = QFileDialog()
        options = dialog.Options()
        file_name = dialog.getOpenFileName(
            self, self.title, os.environ['HOME'],
            f"{self.file_type.upper()} Files (*.{self.file_type})",
            options=options)
        if file_name[0]:
            return file_name[0]


class Inspector(QDockWidget):
    """
    Developer Tools
    """
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName("Dev Tools")
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea
            )
