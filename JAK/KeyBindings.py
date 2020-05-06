#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

from JAK.Utils import Instance, bindings
if bindings() == "PyQt5":
    from PyQt5.QtCore import Qt
else:
    from PySide2.QtCore import Qt


class KeyPress:
    """ #### Imports: from JAK.Keybindings import KeyPress """

    def __init__(self, event, config):
        # * self.win = QMainWindow Instance
        # * self.view = QTWebEngine Instance
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_F11:
                if config['webview']["online"] is True or config['window']["showHelpMenu"] is True:
                    self.full_screen()
            elif event.key() == Qt.Key_F10:
                if config['webview']["online"] is True or config['window']["showHelpMenu"] is True:
                    self.win = Instance.retrieve("win")
                    self.win.corner_window()

            elif event.modifiers() == Qt.ControlModifier:

                if event.key() == Qt.Key_Minus:
                    self._zoom_out()

                elif event.key() == Qt.Key_Equal:
                    self._zoom_in()

    def _current_zoom(self):
        self.view = Instance.retrieve("view")
        return self.view.zoomFactor()

    def _zoom_in(self):
        new_zoom = self._current_zoom() * 1.5
        self.view.setZoomFactor(new_zoom)
        self._save_zoom()

    def _zoom_out(self):
        new_zoom = self._current_zoom() / 1.5
        self.view.setZoomFactor(new_zoom)
        self._save_zoom()

    # TODO only zoom to a certain lvl then reset
    def _reset_zoom(self):
        self.view.setZoomFactor(1)

    def _save_zoom(self):
        percent = int(self._current_zoom() * 100)
        print(f"Zoom:{percent}%")
        # TODO save zoom

    def full_screen(self):
        # TODO animate window resize
        self.win = Instance.retrieve("win")
        if self.win.isFullScreen():
            self.win.showNormal()
            self.win.hide_show_bar()
        else:
            self.win.showFullScreen()
            self.win.hide_show_bar()

