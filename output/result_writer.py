#!/usr/bin/env python3

from typing import Tuple
import datetime
import os
import csv
from matplotlib import pyplot as plt

from db.context import DataContext


class ResultWriter:

    def __init__(self, context: DataContext) -> None:
        self.ctx = context
        self.x = []
        with open("calibration", "r") as cal:
            for line in cal.readlines():
                self.x.append(float(line))

    def transform(self, x):
        result = 0
        for i in range(len(self.x)):
            result += self.x[i]*(x**(len(self.x)-i-1))
        return result

    def calculate_position(self, positions: Tuple[float, float], fallback: float = -10000) -> Tuple[float, float]:
        k1, k2 = positions
        if k1 is not None:
            k1 = self.transform(k1)
        else:
            k1 = fallback
        if k2 is not None:
            k2 = self.transform(k2)
        else:
            k2 = fallback
        return k1, k2

    def plot(self, date: str,fallback:float=-10000)->None:
        measurements = self.ctx.get_measurements_for_day(date)
        orderedMeasurements = {}
        for (time, k1, k2) in measurements:
            orderedMeasurements[time] = (k1, k2)
        start_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        y1 = []
        y2 = []
        x1 = []
        x2 = []
        for time in (start_date+datetime.timedelta(seconds=n) for n in range(24*60*60)):
            timestamp = datetime.datetime.strftime(time, "'%Y-%m-%d_%H-%M-%S")
            key = str(time)
            if key in orderedMeasurements:
                m = orderedMeasurements[key]
                k1, k2 = self.calculate_position(m, fallback=None)
                y1.append(timestamp)
                y2.append(timestamp)
                if k1 is not None:
                    x1.append(k1)
                else:
                    x1.append(fallback)
                if k2 is not None:
                    x2.append(k2)
                else:
                    x2.append(fallback)
            else:
                y1.append(timestamp)
                y2.append(timestamp)
                x1.append(fallback)
                x2.append(fallback)
        plt.plot(x2, marker='o')
        plt.show()

    def write_results(self, path: str, fallback: float = -10000) -> None:
        days = self.ctx.get_days()
        fieldnames = ['timestamp', 'position1', "position2"]
        for day in days:
            print(day)
            with open(os.path.join(path, day+".csv"), "w", newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

                writer.writeheader()
                measurements = self.ctx.get_measurements_for_day(day)
                orderedMeasurements = {}
                for (time, k1, k2) in measurements:
                    orderedMeasurements[time] = (k1, k2)
                start_date = datetime.datetime.strptime(day, '%Y-%m-%d')
                for time in (start_date+datetime.timedelta(seconds=n) for n in range(24*60*60)):
                    timestamp = datetime.datetime.strftime(time, "'%Y-%m-%d_%H-%M-%S")
                    key = str(time)
                    if key in orderedMeasurements:
                        m = orderedMeasurements[key]
                        k1, k2 = self.calculate_position(m, fallback)
                        if k1 is not None:
                            k1 = str(k1).replace(".", ",")
                        if k2 is not None:
                            k2 = str(k2).replace(".", ",")
                        writer.writerow({'timestamp': timestamp, 'position1': k1, "position2": k2})
                    else:
                        writer.writerow({'timestamp': timestamp, 'position1': fallback, "position2": fallback})
