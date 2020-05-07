Just Another Desktop Environment Application Kit ( JAK )

Build web wrappers or hybrid web/desktop applications on Linux, using Python/JavaScript/HTML5/CSS3 powered by [QTWebengine](https://wiki.qt.io/QtWebEngine). Using web technologies we can create beautiful User Interfaces using a diverse amount of available library's and frameworks.

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c79991176d484d50960a36007749b6a6)](https://www.codacy.com/app/codesardine/Jade-Application-Kit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codesardine/Jade-Application-Kit&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/codesardine/Jade-Application-Kit.svg?branch=master)](https://travis-ci.org/codesardine/Jade-Application-Kit)
[![PyPI version](https://badge.fury.io/py/Jade-Application-Kit.svg)](https://badge.fury.io/py/Jade-Application-Kit)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/JustAnotherDesktopEnviroment/Lobby)
![release](https://img.shields.io/github/release/codesardine/jade-application-kit.svg)
![License](https://img.shields.io/github/license/codesardine/jade-application-kit.svg)

[![Packaging status](https://repology.org/badge/vertical-allrepos/python:jade-application-kit.svg)](https://repology.org/metapackage/python:jade-application-kit)

## Getting Started

* Prerequisites
* Python  >= 3.8
* PySide2 >= 5.14 or PyQt5 >= 5.13
* desktop-file-utils, for application.desktop creation: optional

```bash
git clone https://github.com/codesardine/Jade-Application-Kit.git

cd Jade-Application-Kit
```

Install using pip
```bash
pip install -r requirements.txt
```
or
```bash
pip install Jade-Application-Kit
```

Install manually
```bash
~/.virtualenv/python setup.py install
```
or
```bash
sudo setup.py install
```

Install in Manjaro
```bash
sudo pacman -S python-jade-application-kit
```

## Environment variables
JAK defaults to using PySide2 to use PyQt5 set this environment variable, this is read before the config file.
```
export JAK_PREFERRED_BINDING=PyQt5
```

## Config file
Setting bindings via config file, system wide is fetched last.
* User file location = /username/.config/jak.conf
* System wide location = /etc/jak.conf

Config file contents.
```
[bindings]
JAK_PREFERRED_BINDING = PyQt5
```

## Contributing
Please read [CONTRIBUTING.md](https://github.com/codesardine/Jade-Application-Kit/blob/master/CONTRIBUTING.md) for details on code of conduct, and the process for submitting pull requests.

## Using from the command line
With the command line utility you can create a self-contained web wrapper's in a question of seconds.
```
jak-cli --url https://my-web-app-url  --title Mytitle
```
Creating Desktop files in the user directory ( ~/.local/share/applications ).
```
jak-cli --url https://slack.com --title Slack --cde --desc "Collaboration software for connected teams."
```
More options.
```
jak-cli --help
```

## Using Python
```
#!/usr/bin/env python
from JAK.Application import JWebApp

url = "https://my-web-app-url"

webapp = JWebApp(title="Mytitle", online=True, web_contents=url)

webapp.run()
```
### URL Rules:
* We can match domains by starting letters or using Python regex.
* Block Rules: blocks any domain in the list.
* WebBrowserWindow Rules: deny any domain in the list.
* WebBrowserTab Rules: only allow domains in the list, if empty all are allowed, if they start with https:// they open in a new window.

Looking for wrapper's examples? Check [Branches](https://github.com/codesardine/Jade-Application-Kit/branches) starting with `wrapper/`.

#### Api
* [Application](https://codesardine.github.io/Jade-Application-Kit/docs/Application.html)
* [IPC](https://codesardine.github.io/Jade-Application-Kit/docs/IPC.html)
* [KeyBindings](https://codesardine.github.io/Jade-Application-Kit/docs/KeyBindings.html)
* [RequestInterceptor](https://codesardine.github.io/Jade-Application-Kit/docs/RequestInterceptor.html)
* [Utils](https://codesardine.github.io/Jade-Application-Kit/docs/Utils.html)
* [WebEngine](https://codesardine.github.io/Jade-Application-Kit/docs/WebEngine.html)
* [DevTools](https://codesardine.github.io/Jade-Application-Kit/docs/DevTools.html)
* [Settings](https://codesardine.github.io/Jade-Application-Kit/docs/Settings.html)

## Versioning

[SemVer](http://semver.org/) is used for versioning. For the versions available, see the [tags on this repository](https://github.com/codesardine/Jade-Application-Kit/tags).

## Authors

* **Vitor Lopes** - [Twitter Codesardine](https://twitter.com/codesardine)

See also the list of [contributors](https://github.com/codesardine/Jade-Application-Kit/graphs/contributors) who participated in this project.


## Acknowledgments

Applications
* [Just Another Desktop Environment](https://github.com/codesardine/Jadesktop)

Wrappers
* [Microsoft Office online](https://github.com/codesardine/Jade-Application-Kit/tree/wrapper/microsoft-office-online) for [Manjaro](https://manjaro.org)
* [Slack online](https://github.com/codesardine/Jade-Application-Kit/tree/wrapper/slack-online)
* [Skype online](https://github.com/codesardine/Jade-Application-Kit/tree/wrapper/skype-online)
* [Udemy online](https://github.com/Steffan153/udemy-online) by [Caleb Miller](https://github.com/Steffan153)
* [WhatsApp online](https://github.com/codesardine/Jade-Application-Kit/tree/wrapper/whatsapp-online)

Missing yours?, let me know.

## Known Issues
 * Does not like NVIDIA cards and as such falls back to software rendering, so if you use one of them you have to do without GPU acceleration. Only PCI devices.
 * As of Python 3.8 PySide2 is not compatible = https://github.com/codesardine/Jade-Application-Kit/issues/67, until this is fixed upstream set bindings via environment variable or config file.

## License
Jade Application Kit is covered by the GPL license.

Copyright (c) 2015-2019, Vitor Lopes. All rights reserved.

