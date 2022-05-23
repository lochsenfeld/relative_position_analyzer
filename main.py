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
    path = "D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_22-59-41.mp4"
    processor.analyze(path)

    print("running main")


if __name__ == "__main__":
    main()
