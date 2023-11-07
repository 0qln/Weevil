from threading import Thread

class ThreadPtr:
    def __init__(self):
        self.thread = None

    def setValue(self, value:Thread):
        self.thread = value

    def getValue(self) -> Thread:
        return self.thread