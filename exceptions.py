class HttpTimeout(Exception):
    def __init__(self, message, proxy=None, url=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.proxy = proxy
        self.url = url


class BadStatus(Exception):
    def __init__(self, message, proxy=None, url=None, status=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.proxy = proxy
        self.url = url
        self.status = status
