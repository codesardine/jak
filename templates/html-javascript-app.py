#!/usr/bin/env python3
# coding: utf-8
try:
    from j.AK import Api, AppWindow

except Exception as err:
    print("Ops something went wrong: " + str(err))


AK.Api.html = """

<h1>jade Application Kit rocks</h1>
<p>hey my app is great<p>

"""

AK.Api.javascript += """

alert("Testing JavaScript");

"""
AK.main()
