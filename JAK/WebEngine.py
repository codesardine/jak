#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me
import os
from functools import lru_cache as cache
from JAK.Utils import check_url_rules, get_current_path, bindings
from JAK.RequestInterceptor import Interceptor
if bindings() == "PyQt5":
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
else:
    from PySide2.QtCore import QUrl, Qt
    from PySide2.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings


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
            # * Link's that starts with [ ipc:somefunction() ] trigger's the two way communication system between
            # HTML and Python, only if online is set to false
            from JAK.IPC import Communication
            Communication().activate(url)
            return


class JWebPage(QWebEnginePage):
    """ #### Imports: from JAK.WebEngine import JWebPage """
    def __init__(self, profile, webview, config):
        self.config = config
        """
        * :param icon: str
        * :param debug: bool
        * :param online: bool
        * :param url_rules: dict
        """
        super(JWebPage, self).__init__(profile, webview)
        self.featurePermissionRequested.connect(self._on_feature_permission_requested)

    def _open_in_browser(self) -> None:
        """ Open url in a external browser """
        print("Open above^ tab in Browser")
        from webbrowser import open_new_tab
        open_new_tab(self.url)

    def _dialog_open_in_browser(self) -> None:
        """ Opens a dialog to confirm if user wants to open url in external browser """
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
        self.page = JWebPage(self.profile(), self.view(), self.config)
        # Redirect new tabs to same window
        self.page.urlChanged.connect(self._on_url_changed)
        dev_tools = f"http://127.0.0.1:{self.config['debug_port']}/"

        if self.config["online"] and self.url != dev_tools:
            if _type == QWebEnginePage.WebWindowType.WebBrowserTab:
                if self.config["url_rules"]:
                    # Check for URL rules on new tabs
                    if self.url.startswith(self.config["url_rules"]["WebBrowserTab"]):
                        self.open_window(self.url)
                        return False
                    elif check_url_rules("WebBrowserTab", self.url, self.config["url_rules"]):
                        print(f"Redirecting WebBrowserTab^ to same window")
                        return True
                    else:
                        print(f"Deny WebBrowserTab:{self.url}")
                        # check against WebBrowserWindow list to avoid duplicate dialogs
                        if not check_url_rules("WebBrowserWindow", self.url, self.config["url_rules"]):
                            self._dialog_open_in_browser()
                        return False
                else:
                    return True

            elif _type == QWebEnginePage.WebBrowserBackgroundTab:
                print(f"WebBrowserBackgroundTab request:{self.url}")
                return True

            elif _type == QWebEnginePage.WebBrowserWindow:
                if self.config["url_rules"] and self.config["online"]:
                    # Check URL rules on new windows
                    if check_url_rules("WebBrowserWindow", self.url, self.config["url_rules"]):
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

        def grant_permission():
            self.setFeaturePermission(security_origin, feature, self.PermissionGrantedByUser)
        def deny_permission():
            self.setFeaturePermission(security_origin, feature, self.PermissionDeniedByUser)

        if feature == self.Notifications:
            grant_permission()
        elif feature == self.MediaAudioVideoCapture and self.config["MediaAudioVideoCapture"]:
            grant_permission()
        elif feature == self.MediaVideoCapture and self.config["MediaVideoCapture"]:
            grant_permission()
        elif feature == self.MediaAudioCapture and self.config["MediaAudioCapture"]:
            grant_permission()
        elif feature == self.Geolocation and self.config["Geolocation"]:
            grant_permission()
        elif feature == self.MouseLock and self.config["MouseLock"]:
            grant_permission()
        elif feature == self.DesktopVideoCapture and self.config["DesktopVideoCapture"]:
            grant_permission()
        elif feature == self.DesktopAudioVideoCapture and self.config["DesktopAudioVideoCapture"]:
            grant_permission()
        else:
            deny_permission()

    def open_window(self, url):
        """ Open a New Window"""
        # FIXME cookies path needs to be declared for this to work
        self.popup = JWebView(self.config)
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
    def __init__(self, config):
        self.config = config
        super(JWebView, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.profile = QWebEngineProfile.defaultProfile()
        self.webpage = JWebPage(self.profile, self, config)
        self.setPage(self.webpage)
        if config["inject_JavaScript"]["JavaScript"]:
            from JAK.Utils import JavaScript
            JavaScript.inject(self.page(), config["inject_JavaScript"])
        self.interceptor = Interceptor(config)

        if config["user_agent"]:
            # Set user agent
            self.profile.setHttpUserAgent(config["user_agent"])

        if config["debug"]:
            self.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        else:
            self.setContextMenuPolicy(Qt.PreventContextMenu)

        if config["transparent"]:
            # Activates background transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.page().setBackgroundColor(Qt.transparent)
            self.setStyleSheet("background:transparent;")
            print("Transparency detected, make sure you set [ body {background:transparent;} ]")

        # * Set Engine options
        if self.config["JavascriptCanPaste"]:
            self.settings().setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.JavascriptCanPaste, False)
        if self.config["PlaybackRequiresUserGesture"]:
            self.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        if self.config["FullScreenSupportEnabled"]:
            self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        if self.config["AllowWindowActivationFromJavaScript"]:
            self.settings().setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, False)
        if self.config["LocalContentCanAccessRemoteUrls"]:
            self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        if self.config["JavascriptCanAccessClipboard"]:
            self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        if self.config["SpatialNavigationEnabled"]:
            self.settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, False)
        if self.config["TouchIconsEnabled"]:
            self.settings().setAttribute(QWebEngineSettings.TouchIconsEnabled, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.TouchIconsEnabled, False)
        if self.config["FocusOnNavigationEnabled"]:
            self.settings().setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        else:
            self.settings().setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, False)

        if config["online"]:
            self.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
            print("Engine online (IPC) Disabled")
            self.page().profile().downloadRequested.connect(self._download_requested)

            # Set persistent cookies
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

            # set cookies on user folder
            if config["cookies_path"]:
                # allow specific path per application.
                _cookies_path = f"{os.getenv('HOME')}/.jak/{config['cookies_path']}"
            else:
                # use separate cookies database per application
                title = config["title"].lower().replace(" ", "-")
                _cookies_path = f"{os.getenv('HOME')}/.jak/{title}"

            self.profile.setPersistentStoragePath(_cookies_path)
            print(f"Cookies PATH:{_cookies_path}")
        else:
            self.settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
            print("Engine interprocess communication (IPC) up and running:")
            self._ipc_scheme_handler = IpcSchemeHandler()
            self.profile.installUrlSchemeHandler('ipc'.encode(), self._ipc_scheme_handler)
            if config["webChannel"]["active"]:
                from JAK.Utils import JavaScript
                if bindings() == "PyQt5":
                    from PyQt5.QtCore import QFile, QIODevice
                    from PyQt5.QtWebChannel import QWebChannel

                webchannel_js = QFile(':/qtwebchannel/qwebchannel.js')
                webchannel_js.open(QIODevice.ReadOnly)
                webchannel_js = bytes(webchannel_js.readAll()).decode('utf-8')
                webchannel_js += """ var JAK;
                                      new QWebChannel(qt.webChannelTransport, function (channel) {
                                      JAK = channel.objects.Bridge;
                                      });"""

                JavaScript.inject(self.page(), {
                    "JavaScript": webchannel_js,
                    "name": "QWebChannel API"
                })
                self.channel = QWebChannel(self.page())
                if config["webChannel"]["shared_obj"]:
                    self.bridge_obj = config["webChannel"]["shared_obj"]
                else:
                    raise NotImplementedError("QWebChannel shared QObject")

                self.channel.registerObject("Bridge", self.bridge_obj)
                self.page().setWebChannel(self.channel)
                print("QWebChannel bridge active")

        self.profile.setRequestInterceptor(self.interceptor)
        print(self.profile.httpUserAgent())
        validate_url(self, config["web_contents"])

    def _download_requested(self, download_item) -> None:
        """
        * If a download is requested call a save file dialog
        * :param download_item: file to be downloaded
        """
        if bindings() == "PyQt5":
            from PyQt5.QtWidgets import QFileDialog
        else:
            from PySide2.QtWidgets import QFileDialog
        dialog = QFileDialog(self)
        path = dialog.getSaveFileName(dialog, "Save File", download_item.path())

        if path[0]:
            download_item.setPath(path[0])
            print(f"downloading file to:( {download_item.path()} )")
            download_item.accept()
            self.download_item = download_item
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
