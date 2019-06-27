#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from JAK.Utils import check_url_rules


class Interceptor(QWebEngineUrlRequestInterceptor):
    #### Imports: from JAK.RequestInterceptor import Interceptor

    def __init__(self, debug, block_rules=""):
        """

        * :param debug:bool:
        * :param block_rules:dict: URL's to block
        """
        super(Interceptor, self).__init__()
        self.debug = debug
        self.block_rules = block_rules

    def interceptRequest(self, info) -> None:
        """
        * All method calls to the profile on the main thread will block until execution of this function is finished.
        * :param info: QWebEngineUrlRequestInfo
        """
        if self.block_rules is not None:
            # If we have any URL's in the block dictionary
            url = info.requestUrl().toString()
            if check_url_rules("Block", url, self.block_rules):
                # block url's
                info.block(True)
                print(f"Blocked:{url}")

        if self.debug:
            url = info.requestUrl().toString()
            resource = info.resourceType()
            if resource == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted link:{url}")

            elif resource != QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                print(f"Intercepted resource:{url}")
