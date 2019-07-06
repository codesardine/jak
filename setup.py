#!/usr/bin/env python
from setuptools import setup
from os import path
#from setuptools import setup, find_packages

readme = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(readme, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
name             = "Jade-Application-Kit",
version          = "v2.0.7",
packages         = ["j", "JAK"],
python_requires  = ">=3.6",
url              = "https://codesardine.github.io/Jade-Application-Kit",
license          = "GPLv2",
author           = "Vitor Lopes",
description      = "Create native web wrappers or write hybrid Desktop applications on Linux,"
                   " with Python, JavaScript, HTML, and Blink",
long_description = long_description,
long_description_content_type='text/markdown',
download_url     = "https://github.com/codesardine/Jade-Application-Kit/zipball/master",
keywords         = ["Jade Application Kit", "gui", "blink", "html5", "web technologies", "javascript", "python",
                    "webgl", "css3", "QTWebEngine", "PySide2", "linux"],
classifiers      = [
"Development Status :: 4 - Beta",
"Intended Audience :: Developers",
"Intended Audience :: End Users/Desktop",
"License :: OSI Approved :: GNU General Public License (GPL) ",
"Operating System :: POSIX :: Linux",
"Environment :: Web Environment",
"Topic :: Desktop Environment",
"Environment :: X11 Applications",
"Programming Language :: Python :: 3.6",
"Topic :: Software Development :: Libraries :: Application Frameworks",
"Topic :: Software Development :: Libraries :: Python Modules",
"Topic :: Software Development :: User Interfaces",
        ],
    data_files=[
    ("/usr/bin/", ["bin/jak"]), ("/usr/bin/", ["bin/jak-cli"])
    ],
)
