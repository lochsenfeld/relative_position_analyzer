#!/usr/bin/env python3

import os
import sys
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


# TODO y immer zwischen 40 und 60

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
    processor.get_static_positions(args.path, calibration_entities)
    csvWriter.write_calibration_result(os.path.dirname(args.inputfile.name), calibration_entities)
    calibrationWriter.write_calibration(calibration_entities)


def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def analyze(args: Namespace) -> None:
    number_of_threads = args.threads
    dataContext = DataContext()
    processor = Processor(dataContext)


def reset(args: Namespace) -> None:
    print("Warning! About to reset DB!")
    res = query_yes_no("Are you sure, that you want to delete the db with all it's data?", default="no")
    if not res:
        return
    os.remove(os.path.join(os.getcwd(), "measurements.db"))


def main():
    parser = ArgumentParser()
    methods = {
        "calibrate": calibrate,
        "analyze": analyze,
        "reset": reset
    }
    parser.add_argument("method", metavar="method", choices=list(methods.keys()), type=str, help="Name of the method to be executed")
    parser.add_argument("-p", "--path", dest="path", type=pathlib.Path, help="path to video files")
    parser.add_argument("-i", "--input", dest="inputfile", type=FileType('r'), help="path to input file", nargs="?")
    parser.add_argument("-t", "--threads", dest="threads", type=int, help="number of threads")
    args = parser.parse_args()
    print(args)

    method = methods[args.method]
    method(args)


if __name__ == "__main__":
    main()
