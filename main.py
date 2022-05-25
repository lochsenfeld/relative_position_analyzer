#!/usr/bin/env python3

from typing import List
from db.context import DataContext
from processing.processor import Processor
import matplotlib.pyplot as plt


# TODO mechanismus: warnungen fehler etc, telegram?
# TODO mehrere kräne


def main():
    dataContext = DataContext()
    processor = Processor(dataContext)
    # processor.test()
    # processor.analyze(path)
    processor.get_static_positions([
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-23-42.mp4", "2022-05-17 16:24:09"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4", "2022-05-17 16:25:55"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4", "2022-05-17 16:26:30"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-28-42.mp4", "2022-05-17 16:29:06"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-29-42.mp4", "2022-05-17 16:29:49"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-30-42.mp4", "2022-05-17 16:31:11"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-31-42.mp4", "2022-05-17 16:31:53")
    ])

    print("running main")


if __name__ == "__main__":
    main()
