import sys, time
from threading import Thread

class LoadingRotationBar():
    def __init__(self) -> None:
        self.is_loading = False
        self.executionThread = Thread(target=self.print_loading)
        self.executionThread.start()

    def print_loading(self):
        i = 0
        self.is_loading = True
        while self.is_loading:
            if i%4 == 0:
                sys.stdout.write("\r/")
            elif i%4 == 1:
                sys.stdout.write("\r-")
            elif i%4 == 2:
                sys.stdout.write("\r\\")
            elif i%4 == 3:
                sys.stdout.write("\r|")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)

    def finish_loading(self):
        self.is_loading = False
        sys.stdout.write("\r")