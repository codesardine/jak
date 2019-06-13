"""
 App Name   - Jade Application Kit
 App Url    - https://codesardine.github.io/Jade-Application-Kit
 Author     - Vitor Lopes -> Copyright (c) 2016 - 2019
 Author Url - https://vitorlopes.me
"""
from PySide2.QtCore import Qt

try:
    # Testing locally
    from Utils import Instance
except ImportError:
    # Production
    from JAK.Utils import Instance


class KeyPressEvent:
    """
    Define Key Bindings
    """

    def __init__(self, event):
        self.win = Instance.retrieve("win")
        self.view = Instance.retrieve("view")

        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_F11:
                self.full_screen()

            elif event.modifiers() == Qt.ControlModifier:

                if event.key() == Qt.Key_Minus:
                    self._zoom_out()

                elif event.key() == Qt.Key_Equal:
                    self._zoom_in()

    def _current_zoom(self):
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
        print(f"{percent}%")

    def full_screen(self):
        # TODO animate window resize
        full_screen = self.win.isFullScreen()
        if full_screen:
            self.win.showNormal()
        else:
            self.win.showFullScreen()
