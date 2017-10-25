#!/usr/bin/env python3
import subprocess, os
url = "https://your-url.com"
os.chdir("/path/to/application-settings.json")
subprocess.call(["jak", url])

