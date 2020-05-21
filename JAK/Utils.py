#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me

import os
import re
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QApplication

register = {}


def create_desktop_entry(url, title, description, icon):
    entry_name = title.replace(" ", "-")
    filename = f"{entry_name}.desktop"
    user_entry_path = f"{str(Path.home())}/.local/share/applications"
    # system_entry_path = f"/usr/share/applications/{file}"

    template = f"""
# Created with JAK url:https://github.com/codesardine/Jade-Application-Kit
[Desktop Entry]
Type=Application
Version=1.0
Name={title}
Comment={description}
Path=/usr/bin
Exec=jak-cli --url {url} --title {title} --icon {icon} --online true
Icon={icon}
Terminal=false
Categories=Network;
""".strip()

    with open(f"{user_entry_path}/{filename}", 'w+') as file:
        file.write(template)
        print(f"Desktop entry created in:{user_entry_path}/{filename}")

    update_database = "update-desktop-database"
    if os.path.isfile(f"/usr/bin/{update_database}"):
        proc = subprocess.run(f"{update_database} {user_entry_path}", shell=True, check=True)
        if proc.returncode == 0:
            print("Database updated.")
    else:
        print("desktop-file-utils:Not installed\nDatabase not updated.")


def getScreenGeometry():
    app = QApplication.instance()
    return app.desktop().screenGeometry()


def bindings():
    environment_var = "JAK_PREFERRED_BINDING"
    try:
        preferred_bindings = os.environ[environment_var]
        return preferred_bindings
    except KeyError:
        user_config_path = f"{str(Path.home())}/.config/jak.conf"
        if os.path.isfile(user_config_path):
            config_file = user_config_path
        else:
            system_config_path = "/etc/jak.conf"
            config_file = system_config_path
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file)
            preferred_bindings = config["bindings"][environment_var]
            return preferred_bindings
        except Exception as error:
            print(error)


def get_current_path():
    return str(Path('.').absolute())


def check_url_rules(request_type: str, url_request: str, url_rules: tuple) -> bool:
    """
    * Search logic for url rules, we can use regex or simple match the beginning of the domain.
    * :param request_type: WebWindowType
    * :return: function, checks against a list of urls
    """
    SCHEME = "https://"

    if request_type == "Block":
        url_rules=url_rules

    elif request_type == "WebBrowserTab":
        try:
            url_rules = url_rules["WebBrowserTab"]
        except KeyError:
            url_rules = ""

    elif request_type == "WebBrowserWindow":
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
    * :Usage: JavaScript.log(msg)
    """
    @staticmethod
    def log(message: str) -> None:
        """
        * Outputs console.log() messages in the inspector
        * :param message: Log message
        """
        JavaScript.send(f"console.log('JAK log:{message}');")

    @staticmethod
    def css(styles: str, _type) -> None:
        """
        * Insert custom styles
        * :param styles: CSS -> a { color: red; }
        """
        javascript = f"""
             var style = document.createElement('style');
             style.type = 'text/css';
             style.classList.add('{_type}-custom-style');
             style.innerHTML = `{JavaScript._is_file_or_string(styles)}`;
             document.getElementsByTagName('head')[0].appendChild(style);
        """
        view = Instance.retrieve("view")
        view.page().loadFinished.connect(
            lambda: view.page().runJavaScript(javascript)
        )

    @staticmethod
    def alert(message: str) -> None:
        """
        * Triggers an alert message
        * :param message: your popcorn is ready enjoy
        """
        JavaScript.send(f"alert('{message}');")
        JavaScript.log(f"JAK Alert:[{message}]")

    @staticmethod
    def send(script: str) -> None:
        """
        * Send custom JavaScript
        """
        try:
            view = Instance.retrieve("view")
            view.page().runJavaScript(f"{JavaScript._is_file_or_string(script)}")
        except Exception as err:
            print(err)

    @staticmethod
    def inject(page, options: dict) -> None:
        if bindings() == "PyQt5":
            from PyQt5.QtWebEngineWidgets import QWebEngineScript
        else:
            from PySide2.QtWebEngineWidgets import QWebEngineScript

        script = QWebEngineScript()
        script.setName(options["name"])
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setRunsOnSubFrames(True)
        script.setSourceCode(options["JavaScript"])
        print(f"Injecting JavaScript {options['name']}")
        page.profile().scripts().insert(script)

    @staticmethod
    def _is_file_or_string(script) -> str:
        """
        * Detect if is file or string, convert to string
        * :param script: file or string
        """
        if os.path.exists(script) and os.path.isfile(script):
            try:
                with open(script, "r") as file:
                    string = file.read()
                    return string
            except Exception as err:
                print(err)
        elif isinstance(script, str):
            return script
