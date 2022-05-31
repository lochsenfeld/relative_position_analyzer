#!/usr/bin/env python3

from dataclasses import field
import os
import csv
from typing import List

from models.calibration import CalibrationEntity


class CsvWriter:

    # def __init__(self) -> None:

    def write_calibration_result(self, path: str, calibration_entities: List[CalibrationEntity]) -> None:
        fieldnames = ['timestamp', 'position1', "position2", "position1Pxl", "position2Pxl"]
        with open(os.path.join(path, "calibration-result.csv"), "w", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=";")

            writer.writeheader()
            for entity in calibration_entities:
                writer.writerow({'timestamp': entity.timestamp, 'position1': entity.position1_original, "position2": entity.position2_original,
                                 "position1Pxl": entity.position1_calculated, "position2Pxl": entity.position2_calculated})
