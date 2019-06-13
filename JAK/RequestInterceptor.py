"""
 App Name   - Jade Application Kit
 App Url    - https://codesardine.github.io/Jade-Application-Kit
 Author     - Vitor Lopes -> Copyright (c) 2016 - 2019
 Author Url - https://vitorlopes.me
"""
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo


class Interceptor(QWebEngineUrlRequestInterceptor):

    def __init__(self, debug, block_rules=""):
        super(Interceptor, self).__init__()
        self.debug = debug
        self.block_rules = block_rules

    def interceptRequest(self, info) -> None:
        """
        All method calls to the profile on the main thread will block until execution of this function is finished.
        :param info: QWebEngineUrlRequestInfo
        """
        if self.block_rules is not None:
            url = info.requestUrl().toString()
            if url.startswith(tuple("https://" + url for url in self.block_rules)):
                # block urls in the list
                info.block(True)
                print(f"Blocked:{url}")

        if self.debug:
            url = info.requestUrl().toString()
            resource = info.resourceType()
            if resource == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted link:{url}")

            elif resource != QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted resource:{url}")
