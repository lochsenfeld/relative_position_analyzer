#!/usr/bin/env python3

import os
import numpy as np
from typing import List
from matplotlib import pyplot as plt
from models.calibration import CalibrationEntity


class CalibrationWriter:

    def write_calibration(self, calibration_entities: List[CalibrationEntity]) -> None:
        calibration_file = os.path.join(os.getcwd(), "calibration")
        print("Writing calibration to:\t", calibration_file)
        x = []
        y = []
        for entity in calibration_entities:
            if entity.position1_calculated != None and entity.position1_original != None:
                x.append(entity.position1_calculated)
                y.append(entity.position1_original)
            if entity.position2_calculated != None and entity.position2_original != None:
                x.append(entity.position2_calculated)
                y.append(entity.position2_original)
        # plt.plot(x, y, marker='o')
        # plt.show()
        koeff = np.polyfit(x, y, 2)
        poly = np.poly1d(koeff)
        print("polynom is: \n", poly)
        with open(calibration_file, "w") as f:
            f.write(str(poly.coef[2])+"\n")
            f.write(str(poly.coef[1])+"\n")
            f.write(str(poly.coef[0]))
