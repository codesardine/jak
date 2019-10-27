from JAK.Utils import Instance


class Bind:
    """
    Usage: from JAK import IPC
    Create your own class and point to this one: IPC.Bind = MyOverrride
    """
    @staticmethod
    def listener(data):
        # Catch url output
        raise NotImplementedError()


class Communication:
    """
    Call python methods from JavaScript.
    """
    @staticmethod
    def activate(url) -> None:
        """
        :param page: QWebEnginePage
        """
        url = url.split(':')[1]
        if url.endswith("()"):
            try:
                view = Instance.retrieve("view")
                # FIXME This won't allow to pass arguments to the method
                method = Bind.__dict__[url.replace("()", "")]
                method(view)
            except KeyError as error:
                print(error)

            except NameError as error:
                print(error)

        else:
            Bind.listener(url)
