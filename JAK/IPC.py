#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me
from JAK.Utils import Instance


class Bind:
    """
    * Usage: from JAK import IPC
    * Create your own class and point to this one: IPC.Bind = MyOverrride
    """
    @staticmethod
    def listen(data):
        """
        * Do something with the data.
        * :param data:
        * :return: url output
        """
        raise NotImplementedError()


class Communication:
    """
    Call python methods from JavaScript.
    """
    @staticmethod
    def activate(url) -> None:
        if ":" in url:
            url = url.split(':')[1]
        if url.endswith("()"):
            eval(f"Bind.{url}")
        else:
            Bind.listen(url)
