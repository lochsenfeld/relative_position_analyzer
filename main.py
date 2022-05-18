#!/usr/bin/env python3

from processing.processor import Processor
import matplotlib.pyplot as plt


def test():
    plt.figure(figsize=(9, 3))
    plt.grid(True)
    plt.plot([68,
              244,
              531,
              784,
              958,
              1218,
              1425
              ], [472,
                  674,
                  990,
                  1272,
                  1473,
                  1777,
                  2020
                  ], "--bo")
    plt.show()

#TODO mechanismus:
def main():
    processor = Processor()
    path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_22-59-41.mp4"
    processor.analyze(path, "16:24:09")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4"
    # processor.analyze(path, "16:25:55")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4"
    # processor.analyze(path, "16:26:30")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-28-42.mp4"
    # processor.analyze(path, "16:29:06")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-29-42.mp4"
    # processor.analyze(path, "16:29:49")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-30-42.mp4"
    # processor.analyze(path, "16:31:11")

    # path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-31-42.mp4"
    # processor.analyze(path, "16:31:53")

    print("running main")


if __name__ == "__main__":
    main()
