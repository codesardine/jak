#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

from PySide2.QtCore import Qt
from JAK.Utils import Instance


class KeyPress:
    """ #### Imports: from JAK.KeyBindings import KeyPress """

    def __init__(self, event):
        # * self.win = QMainWindow Instance
        # * self.view = QTWebEngine Instance
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_F11:
                self.full_screen()
            elif event.key() == Qt.Key_F12:
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
        self._update_zoom_label()

    def _zoom_out(self):
        new_zoom = self._current_zoom() / 1.5
        self.view.setZoomFactor(new_zoom)
        self._update_zoom_label()

    # TODO only zoom to a certain lvl then reset
    def _reset_zoom(self):
        self.view.setZoomFactor(1)
        self._update_zoom_label()

    def _update_zoom_label(self):
        percent = int(self._current_zoom() * 100)
        print(f"Zoom:{percent}%")

    def full_screen(self):
        # TODO animate window resize
        self.win = Instance.retrieve("win")
        if self.win.isFullScreen():
            self.win.showNormal()
            self.win.hide_show_bar()
        else:
            self.win.showFullScreen()
            self.win.hide_show_bar()

