from distutils.core import setup
from os import path

readme = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(readme, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name             = "Jade-Application-Kit",
	version          = "0.18b2",
	packages         = ["j"],
	url              = "https://codesardine.github.io/Jade-Application-Kit",
	license          = "GPL",
	author           = "Vitor Lopes",
	author_email     = "vmnlop@gmail.com",
	description      = "Build desktop applications using web technologies on Linux, with Python, JavaScript, HTML5, and CSS3 and webkit.",
    long_description = long_description,
    download_url     = "https://github.com/codesardine/Jade-Application-Kit/zipball/master",
    keywords         = ["Jade Application Kit", "gui", "webkit", "html5", "web technologies", "javascript", "python", "webgl", "css3", "pygobject", "gtk", "desktop", "gnome", "linux"],
    classifiers      = [
	    "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Environment :: Web Environment",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
        "Environment :: X11 Applications",
        "Environment :: X11 Applications :: Gnome",
        "Environment :: X11 Applications :: GTK",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        ],
    include_package_data=True,
    package_data={"j":["window.css"]},
    data_files=[
    ("/usr/bin/", ["bin/jak"]),
    ],
)
