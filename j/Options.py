def Cmdl():
    import argparse
    # Create command line options
    option = argparse.ArgumentParser(description='''\
      Jade Application Kit
      --------------------
      Create desktop applications with
      Python, JavaScript and Webkit2
      Author : Vitor Lopes
      Licence: GPLv2
      url: https://codesardine.github.io/Jade-Application-Kit''', epilog='''\
      ex: jak /path/to/my/app/folder
      ex: jak -d http://my-url.com

      Press F11 for distraction free mode
      ''', formatter_class=argparse.RawTextHelpFormatter)
    option.add_argument("-d", "--debug", metavar='\b', help="Enable Developer Tools")
    option.add_argument("-v", "--video", metavar='\b', help="Open a Video Floater on The screen corner")
    option.add_argument('route', nargs="?", help='''\
    Point to your application folder or url!
    ''')
    return option.parse_args()