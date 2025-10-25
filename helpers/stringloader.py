import threading
import time

class SimpleStringLoader():
    def __init__(self,label):
        self.loader = ["=","=","="," "," "," "," "," "," "," "," "," "," "," "," ", " ", " ", " ", " ", " ", " ", " ", " ", " "," " ," ", " ", " ", " ", " ", " "," " ," "]
        self.label = label
        self.running = False
        self.interval = 0.1

        self.direction = 1

    def play(self):
        if self.loader[-1] == "=":
            self.direction = "left"
        elif self.loader[0] == "=":
            self.direction = "right"

        if self.direction == "right":
            val = self.loader.pop(-1)
            self.loader.insert(0,val)
        else:
            val = self.loader.pop(0)
            self.loader.append(val)

        inner = "".join(self.loader)
        self.label.config(text=f"[{inner}]")


    def start(self):
        if not self.running:
            self.running = True
            def helper():
                while self.running:
                    time.sleep(self.interval)
                    self.play()

            th = threading.Thread(target=helper,daemon=True)
            th.start()

    def stop(self):
        self.running = False
