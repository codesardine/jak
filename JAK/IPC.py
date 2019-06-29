try:
    # Testing locally
    from Utils import JavaScript
except ImportError:
    # Production
    from JAK.Utils import JavaScript


class JavaScriptBindings:
    """
    ipc testing
    """
    @staticmethod
    def bind():
        functions = "test()", "failtest()"
        return functions

    def test(self):
        print("send test from JavaScriptBindings.test()")


class _Communication:
    """
    Browser build in IPC communication allows for calling a python function from JavaScript, this needs rework
    """
    @staticmethod
    def _ipc_call(url: str) -> str:
        # remove ipc:
        call = url.split(':')[1]
        return call

    @staticmethod
    def activate(page: object, url) -> None:
        """
        :param page: QWebEnginePage
        """
        for _function in JavaScriptBindings.bind():
            # If there is a match between clicked url and a python function,
            # that function is executed as long as is added to the tuple in ( Bindings.bind() )
            if _Communication._ipc_call(url) == _function:
                function = _function.replace("()", "")
                error_msg = f"This method: {_function} is Not Implemented yet"
                try:
                    msg = f"(IPC) invoking: {_function} from JavaScript"
                    print(msg)
                    JavaScript.log(page.view(), msg)
                    method = JavaScriptBindings.__dict__[function]
                    method(page)
                except KeyError as error:
                    print(f"KeyError: {error}/{error_msg}")

                except NameError as error:
                    print(f"NameError {error}/{error_msg}")
