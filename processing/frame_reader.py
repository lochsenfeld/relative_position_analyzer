#!/usr/bin/env python3
from queue import Queue
from threading import Thread
import cv2


class FrameReader:
    def __init__(self, path, queueSize=128):
        self.stream = cv2.VideoCapture(path)
        self.stopped = False

        self.Q = Queue(maxsize=queueSize)
        self.t = Thread(target=self.update, args=())

    def start(self):

        self.t.daemon = True
        self.t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            if not self.Q.full():
                (grabbed, frame) = self.stream.read()

                if not grabbed:
                    self.stop()
                    return
                frame = frame[532:555, 0:-1]

                # scale_percent = 60 # percent of original size
                # width = int(frame.shape[1] * scale_percent / 100)
                # height = int(frame.shape[0] * scale_percent / 100)
                # dim = (width, height)
                # frame = cv2.resize(frame,dim)
                self.Q.put(frame)

    def read(self):
        return self.Q.get(block=True, timeout=2.0)

    def more(self):
        return not self.stopped

    def stop(self):
        self.stopped = True

    @property
    def fps(self):
        return self.stream.get(cv2.CAP_PROP_FPS)

    @property
    def fpsCount(self):
        return int(self.stream.get(cv2.CAP_PROP_FRAME_COUNT))
