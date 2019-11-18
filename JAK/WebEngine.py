#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me
import os
import time
from functools import lru_cache as cache
from JAK.Utils import JavaScript, check_url_rules, get_current_path, bindings
from JAK.RequestInterceptor import Interceptor
if bindings() == "PyQt5":
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
else:
    from Pyside2.QtCore import QUrl, Qt
    from Pyside2.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from Pyside2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings


@cache(maxsize=5)
def validate_url(self, url: str) -> None:
    """
    * Check if is a URL or HTML and if is valid
    * :param self: QWebEnginePage
    * :param web_contents: URL or HTML
    """
    if "!doctype" in url.lower():
        # Inject HTML
        base_url = get_current_path()
        self.setHtml(url, QUrl(f"file://{base_url}/"))
        print("Loading local HTML")
    else:
        if url.endswith(".html"):
            # HTML file
            if not url.startswith("/"):
                url = f"/{url}"
            url = f"file://{url}"

        elif "://" not in url:
            # HTML URL
            url = f"https://{url}"

        url = QUrl(url)
        if url.isValid():
            self.load(url)
            print(f"Loading URL:{url.toString()}")


class IpcSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self):
        super().__init__()

    def requestStarted(self, request):
        url = request.requestUrl().toString()
        if url.startswith("ipc:"):
                # * Link's that starts with [ ipc:somefunction() ] trigger's the two way communication system bettwen HTML
                # and Python, only if online is set to false
                from JAK.IPC import Communication
                Communication().activate(url)
                return 


class JWebPage(QWebEnginePage):
    """ #### Imports: from JAK.WebEngine import JWebPage """
    def __init__(self, profile, webview, icon, debug, online, cookies_path, url_rules="", ):
        """
        * :param icon: str
        * :param debug: bool
        * :param online: bool
        * :param url_rules: dict
        """
        super(JWebPage, self).__init__(profile, webview)
        self.debug = debug
        self.online = online
        self.url_rules = url_rules
        self.icon = icon
        self.cookies_path = cookies_path
        self.featurePermissionRequested.connect(self._on_feature_permission_requested)

    def _open_in_browser(self) -> None:
        """ Open url in a external browser """
        print("Open above^ tab in Browser")
        from webbrowser import open_new_tab
        open_new_tab(self.url)

    def _dialog_open_in_browser(self) -> None:
        """ Opens a dialog to confirm if user wants to open url in external browser """
        try:
            from Widgets import JCancelConfirmDialog
        except ImportError:
            from JAK.Widgets import JCancelConfirmDialog

        msg = "Open In Your Browser"

        JCancelConfirmDialog(self.parent(), self.title(), msg, self._open_in_browser)

    @cache(maxsize=10)
    def acceptNavigationRequest(self, url, _type, is_main_frame) -> bool:
        """
        * Decide if we navigate to a URL
        * :param url: QtCore.QUrl
        * :param _type: QWebEnginePage.NavigationType
        * :param is_main_frame:bool
        """
        self.url = url.toString()
        self.page = JWebPage(self.profile(), self.view(), self.icon, self.debug, self.online, self.url_rules)
        # Redirect new tabs to same window
        self.page.urlChanged.connect(self._on_url_changed)

        if self.online:
            if _type == QWebEnginePage.WebWindowType.WebBrowserTab:
                if self.url_rules and self.online:
                    # Check for URL rules on new tabs
                    if self.url.startswith(self.url_rules["WebBrowserTab"]):
                        self.open_window(self.url)
                        return False
                    elif check_url_rules("WebBrowserTab", self.url, self.url_rules):
                        print(f"Redirecting WebBrowserTab^ to same window")
                        return True
                    else:
                        print(f"Deny WebBrowserTab:{self.url}")
                        # check against WebBrowserWindow list to avoid duplicate dialogs
                        if not check_url_rules("WebBrowserWindow", self.url, self.url_rules):
                            self._dialog_open_in_browser()
                        return False
                else:
                    return True

            elif _type == QWebEnginePage.WebBrowserBackgroundTab:
                print(f"WebBrowserBackgroundTab request:{self.url}")
                return True

            elif _type == QWebEnginePage.WebBrowserWindow:
                if self.url_rules and self.online:
                    # Check URL rules on new windows
                    if check_url_rules("WebBrowserWindow", self.url, self.url_rules):
                        print(f"Deny WebBrowserWindow:{self.url}")
                        self._dialog_open_in_browser()
                        return False
                    else:
                        print(f"Allow WebBrowserWindow:{self.url}")
                        return True
                else:
                    return True

            elif _type == QWebEnginePage.WebDialog:
                return True
        return True

    def _on_feature_permission_requested(self, security_origin, feature):
        if feature is self.Notifications:
            self.setFeaturePermission(security_origin, feature, self.PermissionGrantedByUser)

    def open_window(self, url):
        """ Open a New Window"""
        # FIXME cookies path needs to be declared for this to work
        self.popup = JWebView(web_contents=url, online=True, cookies_path=self.cookies_path)
        self.popup.page().windowCloseRequested.connect(self.popup.close)
        self.popup.show()
        print(f"Opening New Window^")

    @cache(maxsize=2)
    def createWindow(self, _type: object) -> QWebEnginePage:
        """
        * Redirect new window's or tab's to same window
        * :param _type: QWebEnginePage.WebWindowType
        """
        return self.page

    def _on_url_changed(self, url: str) -> None:
        url = url.toString()
        if url == "about:blank":
            return False
        else:
            validate_url(self, url)


class JWebView(QWebEngineView):
    """ #### Imports: from JAK.WebEngine import JWebView """
    def __init__(self, title="", icon="", web_contents="", debug=False, transparent=False, online=False, url_rules="",
                 cookies_path="", user_agent="", custom_css="", custom_js=""):
        """
        * :param title:str
        * :param icon:str
        * :param web_contents:str
        * :param debug:bool
        * :param transparent:bool
        * :param online:bool
        * :param disable_gpu:bool
        * :param url_rules:dict
        * :param cookies_path:str
        * :param user_agent:str
        * :param custom_css:str
        * :param custom_js:str
        * :param toolbar:dict
        """
        super(JWebView, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.debug = debug
        self.online = online
        self.home = web_contents
        self.profile = QWebEngineProfile.defaultProfile()
        self.webpage = JWebPage(self.profile, self, icon, debug, online, cookies_path, url_rules)
        self.setPage(self.webpage)
        self.page().loadFinished.connect(self._page_load_finish)
        #QWebEnginePage.setDevToolsPage(self.page)
        if custom_css:
            # Check for custom CSS
            self.custom_css = custom_css
            print("Custom CSS detected")

        if custom_js:
            # Check for custom JavaScript
            self.custom_js = custom_js
            print("Custom JavaScript detected")

        if url_rules:
            # Check for URL rules
            try:
                self.block_rules = url_rules["block"]
            except KeyError:
                self.block_rules = ""
            finally:
                self.interceptor = Interceptor(debug, self.block_rules)
        else:
            self.interceptor = Interceptor(debug)

        if user_agent:
            # Set user agent
            self.user_agent = user_agent
            self.profile.setHttpUserAgent(user_agent)

        if self.debug:
            self.page().setInspectedPage(self.webpage)
            self.triggerPageAction(QWebEnginePage.InspectElement)
            self.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        else:
            self.setContextMenuPolicy(Qt.PreventContextMenu)

        if transparent:
            # Activates background transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.page().setBackgroundColor(Qt.transparent)
            self.setStyleSheet("background:transparent;")
            print("Transparency detected, make sure you set [ body {background:transparent;} ]")

        settings = self.settings()
        # * Set Engine options
        # * TODO: allow to set settings per application by passing a list
        settings.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.TouchIconsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        if online:
            settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
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

            self.profile.setPersistentStoragePath(_cookies_path)
            print(f"Cookies PATH:{_cookies_path}")
        else:
            settings.setAttribute(QWebEngineSettings.ShowScrollBars, False)
            print("Engine interprocess communication (IPC) up and running:")
            #self.profile.setHttpCacheType(self.profile.MemoryHttpCache)
            self._ipc_scheme_handler = IpcSchemeHandler()
            self.profile.installUrlSchemeHandler('ipc'.encode(), self._ipc_scheme_handler)

        self.profile.setRequestInterceptor(self.interceptor)
        print(self.profile.httpUserAgent())
        validate_url(self, web_contents)

    def _page_load_finish(self) -> None:
        result = time.localtime(time.time())
        print(f"Document Ready in: {result.tm_sec} seconds")
        try:
            if self.custom_css:
                print("Custom CSS loaded")
                JavaScript.css(self.custom_css)
        except AttributeError:
            pass

        try:
            if self.custom_js:
                print("Custom JavaScript loaded")
                JavaScript.send(self.custom_js)
        except AttributeError:
            pass

    def _download_requested(self, download_item)-> None:
        """
        * If a download is requested call a save file dialog
        * :param download_item: file to be downloaded
        """
        if bindings() == "PyQt5":
            from PyQt5.QtWidgets import QFileDialog
        else:
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
        Goes to previous page and pops an alert informing the user that the download is finish and were to find it
        """
        file_path = self.download_item.path()
        msg = f"File Downloaded to: {file_path}"

        from JAK.Widgets import InfoDialog
        InfoDialog(self, "Download Complete", msg)
        if self.online:
            self.back()

    def navigate_home(self) -> None:
        """
        Goes back to original application url
        """
        self.load(self.home)
