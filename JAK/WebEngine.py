"""
 App Name   - Jade Application Kit
 App Url    - https://codesardine.github.io/Jade-Application-Kit
 Author     - Vitor Lopes -> Copyright (c) 2016 - 2019
 Author Url - https://vitorlopes.me
"""
import os
import time
try:
    # Testing locally
    from Utils import JavaScript
    from RequestInterceptor import Interceptor
except ImportError:
    # Production
    from JAK.Utils import JavaScript
    from JAK.RequestInterceptor import Interceptor

from PySide2.QtCore import QUrl, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings


def validate_url(self, web_contents: str) -> None:
    """
    Check if is a url or HTML
    Check if url is valid

    :param self: QWebEnginePage
    :param web_contents: url or HTML
    :return:
    """
    if "!doctype html" in web_contents.lower():
        self.setHtml(web_contents)
        print("Loading local HTML")
    else:
        url = QUrl(web_contents)
        if url.isValid():
            self.setUrl(web_contents)
            print(f"Loading URL:{url.toString()}")


class JWebPage(QWebEnginePage):

    def __init__(self, icon, debug, online, url_rules="", ):
        super(JWebPage, self).__init__()
        self.debug = debug
        self.online = online
        self.url_rules = url_rules
        self.page = self
        self.icon = icon

    def _open_in_browser(self) -> None:
        """
        Open url in a external browser
        """
        print("Open above^ tab in Browser")
        import webbrowser
        webbrowser.open(self.url().toString())

    def _dialog_open_in_browser(self) -> None:
        """
        Opens a dialog to confirm if user wants to open url in external browser
        """
        try:
            from Widgets import JCancelConfirmDialog
        except ImportError:
            from JAK.Widgets import JCancelConfirmDialog

        msg = "Open In Your Browser"

        JCancelConfirmDialog(self.parent(), self.title(), msg, self._open_in_browser)

    def acceptNavigationRequest(self, url, _type, is_main_frame) -> bool:
        """
        Decide if we go to a url and what to do next

        :param url: PySide2.QtCore.QUrl
        :param _type: QWebEnginePage.NavigationType
        :param is_main_frame: bool
        """
        url = url.toString()
        self.page = JWebPage(self.icon, self.debug, self.online, self.url_rules)
        # Redirect new tabs to same window
        self.page.urlChanged.connect(self._on_url_changed)

        if url == "about:blank":
            return False

        elif not self.online and url.startswith("ipc:"):
            # Clicking a link that starts with [ ipc:somefunction() ] triggers the communication system
            if self.debug:
                print(f"IPC call: {url}")
            try:
                from IPC import _Communication
            except ImportError:
                from JAK.IPC import _Communication

            _Communication().activate(self, url)
            return False

        elif _type == QWebEnginePage.WebWindowType.WebBrowserTab:
            if self.url_rules and self.online:
                # check url list an only load a tab if there is a match
                if url.startswith(tuple(self.scheme_logic("WebBrowserTab"))):
                    print(f"Redirecting WebBrowserTab^ to same window")
                    return True
                else:
                    print(f"Deny WebBrowserTab:{url}")
                    # check against WebBrowserWindow list to avoid duplicate dialogs
                    if not url.startswith(tuple(self.scheme_logic("WebBrowserWindow"))):
                        self._dialog_open_in_browser()
                    return False
            else:
                return True

        elif _type == QWebEnginePage.WebBrowserBackgroundTab:
            print(f"WebBrowserBackgroundTab request:{url}")
            return True

        elif _type == QWebEnginePage.WebBrowserWindow:
            if self.url_rules and self.online:
                # check url list an only deny if there is a match
                if url.startswith(tuple(self.scheme_logic("WebBrowserWindow"))):
                    print(f"Deny WebBrowserWindow:{url}")
                    self._dialog_open_in_browser()
                    return False
                else:
                    print(f"Allow WebBrowserWindow:{url}")
                    return True
            else:
                return True

        elif _type == QWebEnginePage.WebDialog:
            return True

        return True

    def scheme_logic(self, request_type):
        """
        :param request_type: WebWindowType
        :return: a function that check against a list of urls
        """
        SCHEME = "https://"

        if request_type is "WebBrowserTab":
            url_rules = self.url_rules["WebBrowserTab"]

        elif request_type is "WebBrowserWindow":
            url_rules = self.url_rules["WebBrowserWindow"]

        return (f"{SCHEME}{url}" for url in url_rules)

    def createWindow(self, _type: object) -> QWebEnginePage:
        """
        Redirect any new window or tab to same window
        :param _type: PySide2.QtWebEngineWidgets.QWebEnginePage.WebWindowType
        """
        return self.page

    def _on_url_changed(self, url: str) -> None:
        url = url.toString()
        validate_url(self, url)


class JWebView(QWebEngineView):
    """
    Create the browser view
    """
    def __init__(self, title="", icon="", web_contents="", debug=False, transparent=False, online=False, url_rules="",
                 cookies_path="", user_agent="", custom_css="", custom_js=""):

        super(JWebView, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.debug = debug
        self.online = online
        self.home = web_contents
        self.profile = QWebEngineProfile().defaultProfile()
        self.webpage = JWebPage(icon, debug, online, url_rules)
        self.setPage(self.webpage)
        self.page().fullScreenRequested.connect(self._full_screen_requested)
        self.page().loadFinished.connect(self._page_load_finish)
        if custom_css:
            self.custom_css = custom_css
            print("Custom CSS detected")

        if custom_js:
            self.custom_js = custom_js
            print("Custom JavaScript detected")

        if url_rules:
            self.block_rules = url_rules["block"]
            self.interceptor = Interceptor(debug, self.block_rules)
        else:
            self.interceptor = Interceptor(debug)
        self.profile.setRequestInterceptor(self.interceptor)

        if user_agent:
            self.user_agent = user_agent
            self.profile.setHttpUserAgent(user_agent)

        print(self.profile.httpUserAgent())

        if online:
            print("Engine online (IPC) Disabled")
            self.page().profile().downloadRequested.connect(self._download_requested)

            # Set persistent cookies
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

            # set cookies on user folder
            if cookies_path:
                # allow specific path per application.
                _cookies_path = f"{os.getenv('HOME')}/.jak/{cookies_path}"
            else:
                # use separate cookies database per application
                title = title.lower().replace(" ", "-")
                _cookies_path = f"{os.getenv('HOME')}/.jak/{title}"

            self.profile.setCachePath(_cookies_path)
            self.profile.setPersistentStoragePath(_cookies_path)
            print(f"Cookies PATH:{_cookies_path}")
        else:
            print("Engine interprocess communication (IPC) up and running:")
            #self.profile.setHttpCacheType(self.profile.MemoryHttpCache)

        if self.debug:
            # TODO implement webinspector
            self.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        else:
            self.setContextMenuPolicy(Qt.PreventContextMenu)

        if transparent:
            # Activates webview background transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.page().setBackgroundColor(Qt.transparent)
            self.setStyleSheet("background:transparent;")
            print("Transparency detected, make sure you set [ body {background:transparent;} ]")

        settings = self.settings()
        # TODO allow settings per application
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)  # Disabled BUG
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        if online:
            settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)

        validate_url(self, web_contents)

    def _page_load_finish(self) -> None:
        result = time.localtime(time.time())
        print(f"Document Ready in: {result.tm_sec} seconds")
        try:
            if self.custom_css:
                print("Custom CSS loaded")
                JavaScript.css(self, self.custom_css)
        except AttributeError:
            pass

        try:
            if self.custom_js:
                print("Custom JavaScript loaded")
                JavaScript.send(self, self.custom_js)
        except AttributeError:
            pass

    def _full_screen_requested(self, request) -> None:
        # FIXME https://bugreports.qt.io/browse/PYSIDE-930
        request.accept()

    def _download_requested(self, download_item)-> None:
        """
        If a download is requested call a confirmation dialog

        :param download_item: file to be downloaded
        """
        from PySide2.QtWidgets import QFileDialog
        self.download_item = download_item
        dialog = QFileDialog(self)
        path = dialog.getSaveFileName(dialog, "Save File", download_item.path())

        if path[0]:
            print(path)
            download_item.setPath(path[0])
            print(f"downloading file to:( {download_item.path()} )")
            download_item.accept()
            download_item.finished.connect(self._download_finished)

        else:
            print("Download canceled")

    def _download_finished(self) -> None:
        """
        Goes to previous page and pops an alert informing the
        user that the download is finish and were the file is
        """
        file_path = self.download_item.path()
        msg = f"File Downloaded to: {file_path}"

        try:
            from Widgets import InfoDialog
        except ImportError:
            from JAK.Widgets import InfoDialog
        InfoDialog(self, "Download Complete", msg)
        if self.online:
            self.back()

    def navigate_home(self) -> None:
        """
        Goes back to original application url
        """
        self.setUrl(self.home)







