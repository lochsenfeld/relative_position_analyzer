#!/usr/bin/env python3

from ast import arg
from multiprocessing.dummy import Process
import os
from multiprocessing import Pool, Queue
from threading import Thread
import time
from typing import List
from db.context import DataContext
from models.calibration import CalibrationEntity
from output.calibration_writer import CalibrationWriter
from output.csv_writer import CsvWriter
from output.result_writer import ResultWriter
from processing.processor import Processor
import matplotlib.pyplot as plt
from argparse import ArgumentParser, FileType, Namespace
import pathlib
import csv

# 49
# TODO y immer zwischen 40 und 60
# TODO filter dateien


def calibrate(args: Namespace) -> None:
    calibration_entities = []
    with args.inputfile as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            calibration_entities.append(CalibrationEntity(row["timestamp"], float(row["position1"]) if len(row["position1"])
                                                          > 0 else None, float(row["position2"]) if len(row["position2"]) > 0 else None))
    dataContext = DataContext(args.dbPath)
    processor = Processor(dataContext)
    csvWriter = CsvWriter()
    calibrationWriter = CalibrationWriter()
    processor.get_static_positions(args.path, calibration_entities)
    csvWriter.write_calibration_result(os.path.dirname(args.inputfile.name), calibration_entities)
    calibrationWriter.write_calibration(calibration_entities)


def run(dbPath: str, path: str):
    dataContext = DataContext(dbPath)
    processor = Processor(dataContext)
    processor.analyze(path)


def analyze(args: Namespace) -> None:
    number_of_threads = args.threads
    DataContext(args.dbPath)

    files = [os.path.join(args.path, f) for f in os.listdir(args.path)
             if os.path.isfile(os.path.join(args.path, f)) and os.path.splitext(f)[1] == ".mp4"]
    # TODO filtern
    start = time.time()
    # pool = Pool(number_of_threads)
    # processes = [pool.apply_async(run, args=(args.dbPath, f)) for f in files]
    # for p in processes:
    #     p.get()
    
    # for p in files:
    #     run(args.dbPath, p)
    run(args.dbPath, files[0])
    print("took ", time.time()-start)

def output(args: Namespace) -> None:
    dataContext = DataContext(args.dbPath)
    output = ResultWriter(dataContext)
    output.write_results(args.outputPath)

def main():
    parser = ArgumentParser()
    methods = {
        "calibrate": calibrate,
        "analyze": analyze,
        "output": output
    }
    parser.add_argument("method", metavar="method", choices=list(methods.keys()), type=str, help="Name of the method to be executed")
    parser.add_argument("-p", "--path", dest="path", type=pathlib.Path, help="path to video files")
    parser.add_argument("-d", "--dbpath", dest="dbPath", type=pathlib.Path, help="path to sqlite file")
    parser.add_argument("-i", "--input", dest="inputfile", type=FileType('r'), help="path to input file", nargs="?")
    parser.add_argument("-o", "--output", dest="outputPath", type=pathlib.Path, help="path to output dir", nargs="?")
    parser.add_argument("-t", "--threads", dest="threads", type=int, help="number of threads")
    args = parser.parse_args()
    print(args)

    method = methods[args.method]
    method(args)


if __name__ == "__main__":
    main()
