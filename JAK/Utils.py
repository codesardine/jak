# import weakref
import os
register = {}


class Instance:
    """
    Adds created object instances or values in a dictionary, it can be used to point
    to references we don,t want to be garbage collected, for usage later
    :usage: from Jak import Instance
    """

    @staticmethod
    def get_instances() -> dict:
        """
        :usage: Instance.get_instances()
        """
        return register

    @staticmethod
    def record(name: str, _type: object) -> None:
        """
        Should only be used once per instance
        :usage: Instance.record("name", object)
        """
        register[name] = _type
        print(f"Registering ['{name}'] Instance")

    @staticmethod
    def retrieve(name: str) -> object or str:
        """
        :usage: Instance.retrieve("name")
        """
        try:
            return register[name]
        except KeyError:
            print(f"Instance: ['{name}'] Not Present, to add it use -> Instance.record(['{name}', object])")
            return ""

    @staticmethod
    def auto(name: str, _type: object) -> object:
        """
        Automatically detects if the key is present and retrieves it, if not present, creates it and retrieves it,
        should only be used once per instance
        :usage: Instance.auto("name", object)
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
    Run javascript in the webview after load is complete
    Injects will be logged in the inspector

    :imports: from Jak.Utils import JavaScript
    :usage: JavaScript.log(webview:instance, msg)
    """

    @staticmethod
    def log(webview, message: str) -> None:
        """
        Outputs console.log() messages in the inspector

        :param webview: instance
        :param message: foo has finish
        """
        JavaScript.send(webview, f"console.log('JAK log:{message}');")

    @staticmethod
    def css(webview, styles: str) -> None:
        """
        Insert custom styles
        :param webview: instance
        :param styles: CSS -> a { color: red; }
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
        Triggers an alert message
        :param webview: instance
        :param message: your popcorn is ready enjoy
        """
        JavaScript.send(webview, f"alert('{message}');")
        JavaScript.log(webview, f"JAK Alert:[{message}]")

    def send(self, javascript: str) -> None:
        """
        Send custom JavaScript
        :param self: webview instance
        """
        self.page().runJavaScript(f"{JavaScript.detect_type(javascript)}")

    @staticmethod
    def detect_type(inbound) -> str:
        """
        Detect if is file or string, convert to string
        :param inbound: file or string
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


