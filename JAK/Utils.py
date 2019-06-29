#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

import os
import re

register = {}


def check_url_rules(request_type: str, url_request: str, url_rules: tuple) -> bool:
    """
    * Search logic for url rules, we can use regex or simple match the beginning of the domain.
    * :param request_type: WebWindowType
    * :return: function, checks against a list of urls
    """
    SCHEME = "https://"

    if request_type is "Block":
        url_rules=url_rules

    elif request_type is "WebBrowserTab":
        try:
            url_rules = url_rules["WebBrowserTab"]
        except KeyError:
            url_rules = ""

    elif request_type is "WebBrowserWindow":
        try:
            url_rules = url_rules["WebBrowserWindow"]
        except KeyError:
            url_rules = ""

    for rule in url_rules:
        pattern = re.compile(f"{SCHEME}{rule}")
        if url_request.startswith(f"{SCHEME}{rule}"):
            print(f"{SCHEME}{rule}:Method:startswith")
            return True
        elif re.search(pattern, url_request):
                print(f"{SCHEME}{rule}:Method:regex")
                return True
    return False

class Instance:
    """
    #### :Imports: from JAK.Utils import Instance
    Add object instances in a dictionary, it can be used to point
    to references we don,t want to be garbage collected, for usage later
    """

    @staticmethod
    def get_instances() -> dict:
        """
        * :Usage: Instance.get_instances()
        """
        return register

    @staticmethod
    def record(name: str, _type: object) -> None:
        """
        * :Usage: Instance.record("name", object)
        * Should only be used once per instance
        """
        register[name] = _type
        print(f"Registering ['{name}'] Instance")

    @staticmethod
    def retrieve(name: str) -> object or str:
        """
        * :Usage: Instance.retrieve("name")
        """
        try:
            return register[name]
        except KeyError:
            print(f"Instance: ['{name}'] Not Present, to add it use -> Instance.record(['{name}', object])")
            return ""

    @staticmethod
    def auto(name: str, _type: object) -> object:
        """
        * :Usage: Instance.auto("name", object)
        * Automatically detects if an instance is active with that name and retrieves it.
        If not present, creates it creates a new one and retrieves it.
        * Should only be used once per instance
        """
        try:
            return register[name]
        except KeyError:
            register[name] = _type
        finally:
            print(f"Registering and Retrieving ['{name}'] Instance")
            return register[name]


class JavaScript:
    """
    * Run javascript in the webview after load is complete Injects will be logged in the inspector
    * :Imports: from Jak.Utils import JavaScript
    * :Usage: JavaScript.log(webview:instance, msg)
    """

    @staticmethod
    def log(webview, message: str) -> None:
        """
        * Outputs console.log() messages in the inspector
        * :param webview: QWebengineView instance
        * :param message: Log message
        """
        JavaScript.send(webview, f"console.log('JAK log:{message}');")

    @staticmethod
    def css(webview, styles: str) -> None:
        """
        * Insert custom styles
        * :param webview: QWebengineView instance
        * :param styles: CSS -> a { color: red; }
        """
        javascript = f"""
             var style = document.createElement('style');
             style.type = 'text/css';
             style.classList.add('jak-custom-style');
             style.innerHTML = "{JavaScript.detect_type(styles)}";
             document.getElementsByTagName('head')[0].appendChild(style);
        """
        JavaScript.send(webview, javascript)
        JavaScript.log(webview, f"JAK Custom Styles Applied:[{styles}]")

    @staticmethod
    def alert(webview, message: str) -> None:
        """
        * Triggers an alert message
        * :param webview: QWebengineView instance
        * :param message: your popcorn is ready enjoy
        """
        JavaScript.send(webview, f"alert('{message}');")
        JavaScript.log(webview, f"JAK Alert:[{message}]")

    def send(self, javascript: str) -> None:
        """
        * Send custom JavaScript
        * :param self: QWebengineView instance
        """
        self.page().runJavaScript(f"{JavaScript.detect_type(javascript)}")

    @staticmethod
    def detect_type(inbound) -> str:
        """
        * Detect if is file or string, convert to string
        * :param inbound: file or string
        """
        if os.path.exists(inbound) and os.path.isfile(inbound):
            try:
                with open(inbound, "r") as file:
                    string = file.read()
                    return string
            except IOError:
                return False
            return True
        elif isinstance(inbound, str):
            return inbound

        else:
            print("JavaScript.send() error, file path or string.")
