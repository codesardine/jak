import sys
# TODO Decide what is going to be exposed to javascript
html = ""
js = ""


class Fs:
    def open_file(self, access_mode="r"):
        """
            input:  filename and path.
            output: file contents.
        """
        try:
            with open(self, access_mode, encoding='utf-8') as file:
                return file.read()

        except IOError:
            print(self + " File not found.")
            sys.exit(0)
