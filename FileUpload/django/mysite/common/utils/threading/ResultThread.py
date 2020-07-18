import threading


class ResultThread(threading.Thread):
    """重写多线程, 使其能够返回值"""

    def __init__(self, name, target=None, args=()):
        super(ResultThread, self).__init__()
        self.name = name
        self.func = target
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
