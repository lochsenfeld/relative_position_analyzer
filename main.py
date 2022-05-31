#!/usr/bin/env python3

import os
from typing import List
from db.context import DataContext
from models.calibration import CalibrationEntity
from output.calibration_writer import CalibrationWriter
from output.csv_writer import CsvWriter
from processing.processor import Processor
import matplotlib.pyplot as plt
from argparse import ArgumentParser, FileType, Namespace
import pathlib
import csv


#TODO y immer zwischen 40 und 60

def calibrate(args: Namespace) -> None:
    calibration_entities = []
    with args.inputfile as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            calibration_entities.append(CalibrationEntity(row["timestamp"], float(row["position1"]) if len(row["position1"])
                                                          > 0 else None, float(row["position2"]) if len(row["position2"]) > 0 else None))
    dataContext = DataContext()
    processor = Processor(dataContext)
    csvWriter = CsvWriter()
    calibrationWriter = CalibrationWriter()
    processor.get_static_positions(args.path[0], calibration_entities)
    csvWriter.write_calibration_result(os.path.dirname(args.inputfile.name), calibration_entities)
    calibrationWriter.write_calibration(calibration_entities)


def main():
    parser = ArgumentParser()
    methods = {
        "calibrate": calibrate
    }
    parser.add_argument("method", metavar="method", choices=list(methods.keys()), type=str, nargs=1, help="Name of the method to be executed")
    parser.add_argument("-p", "--path", dest="path", type=pathlib.Path, help="path to video files", nargs=1)
    parser.add_argument("-i", "--input", dest="inputfile", type=FileType('r'), help="path to input file", nargs="?")
    args = parser.parse_args()
    print(args)

    method = methods[args.method[0]]
    method(args)
    return

    dataContext = DataContext()
    processor = Processor(dataContext)
    # processor.test()
    # processor.analyze(path)
    processor.get_static_positions([
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-23-42.mp4", "2022-05-17 16:24:09"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4", "2022-05-17 16:25:55"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-25-42.mp4", "2022-05-17 16:26:30"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-28-42.mp4", "2022-05-17 16:29:06"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-29-42.mp4", "2022-05-17 16:29:49"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-30-42.mp4", "2022-05-17 16:31:11"),
        # ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-31-42.mp4", "2022-05-17 16:31:53"),
        ("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_16-35-42.mp4", "2022-05-17 16:36:20")
    ])

    print("running main")


if __name__ == "__main__":
    main()
