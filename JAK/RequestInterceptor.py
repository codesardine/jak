#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

from JAK.Utils import check_url_rules, bindings
if bindings() == "PyQt5":
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
else:
    from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo


class Interceptor(QWebEngineUrlRequestInterceptor):
    #### Imports: from JAK.RequestInterceptor import Interceptor

    def __init__(self, config):
        self.config = config
        """

        * :param debug:bool:
        * :param block_rules:dict: URL's to block
        """
        super(Interceptor, self).__init__()

    def interceptRequest(self, info) -> None:
        """
        * All method calls to the profile on the main thread will block until execution of this function is finished.
        * :param info: QWebEngineUrlRequestInfo
        """

        if self.config['webview']["urlRules"] is not None:
            # If we have any URL's in the block dictionary
            url = info.requestUrl().toString()
            try:
                if check_url_rules("Block", url, self.config['webview']["urlRules"]["block"]):
                    # block url's
                    info.block(True)
                    print(f"Blocked:{url}")
            except KeyError:
                pass

        if self.config["debug"]:
            url = info.requestUrl().toString()
            resource = info.resourceType()
            if resource == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted link:{url}")

            elif resource != QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted resource:{url}")
