## Jade Application Kit ( JAK )

Build web wrappers or hybrid web/desktop applications on Linux, using Python/JavaScript/HTML5/CSS3 powered by [QTWebengine](https://wiki.qt.io/QtWebEngine)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c79991176d484d50960a36007749b6a6)](https://www.codacy.com/app/codesardine/Jade-Application-Kit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=codesardine/Jade-Application-Kit&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/codesardine/Jade-Application-Kit.svg?branch=master)](https://travis-ci.org/codesardine/Jade-Application-Kit)
[![PyPI version](https://badge.fury.io/py/Jade-Application-Kit.svg)](https://badge.fury.io/py/Jade-Application-Kit)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/JustAnotherDesktopEnviroment/Lobby)

[![Packaging status](https://repology.org/badge/vertical-allrepos/python:jade-application-kit.svg)](https://repology.org/metapackage/python:jade-application-kit)

## Getting Started

* Prerequisites
* Python  >= 3.6
* PySide2 >= 5.12.3

```
git clone this_repo_address

cd this_repo_directory_on_your_local_machine
```

Install pip
```
pip install -r requirements.txt

pip install Jade-Application-Kit
```

Install manually
```
~/.virtualenv/python setup.py install or sudo setup.py install
```

Install Manjaro
```
pacman -S python-jade-application-kit
```

## Contributing
Please read [CONTRIBUTING.md](https://github.com/codesardine/Jade-Application-Kit/blob/master/CONTRIBUTING.md) for details on code of conduct, and the process for submitting pull requests.

## Usage
With the command line utility you can create a self-contained web wrapper's in a question of seconds.
```
jak-cli --url https://my-web-app-url  --title Mytitle
```
For more options.
```
jak-cli --help
```

Using Python
```
#!/usr/bin/env python
from JAK.Application import JWebApp

url = "https://my-web-app-url"

webapp = JWebApp(title="Mytitle", online=True, web_contents=url)

webapp.run()
```
Arguments
* title        = boolean
* icon         = string
* web_contents = string
* debug        = boolean
* transparent  = boolean
* online       = boolean
* url_rules    = dictionary
* cookies_path = string
* user_agent   = string
* custom_css   = string
* custom_js    = string
* toolbar      = dictionary

## Versioning

[SemVer](http://semver.org/) is used for versioning. For the versions available, see the [tags on this repository](https://github.com/codesardine/Jade-Application-Kit/tags).

## Authors

* **Vitor Lopes** - [Twitter Codesardine](https://twitter.com/codesardine)

See also the list of [contributors](https://github.com/codesardine/Jade-Application-Kit/graphs/contributors) who participated in this project.


## Acknowledgments

Applications
* [Just Another Desktop Environment](https://github.com/codesardine/Jadesktop)

Wrappers
* [Microsoft Office online](https://gitlab.manjaro.org/applications/ms-office-online-launcher) for Manjaro

Missing yours?, let me know

Using web technologies we can create beautiful User Interfaces using a diverse amount of available web library's.

## License
Jade Application Kit is covered by the GPL license.

Copyright (c) 2015-2019, Vitor Lopes. All rights reserved.

