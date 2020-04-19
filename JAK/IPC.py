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
    def send(url) -> None:
        if ":" in url:
            url = url.split(':')[1]
        if url.endswith("()"):
            eval(f"Bind.{url}")
        else:
            Bind.listen(url)
