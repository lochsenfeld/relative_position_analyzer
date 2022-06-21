#!/usr/bin/env python3
import time
from typing import List, Tuple
import cv2
from ctypes import Array
import numpy as np
import os
import datetime

from db.context import DataContext
from models.calibration import CalibrationEntity
from processing.frame_reader import FrameReader


class Processor:

    def __init__(self, dataContext: DataContext) -> None:
        self.ctx = dataContext

    def get_center_of_mass(self, frame: Array) -> Array:

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([170, 35, 20])
        upper1 = np.array([179, 255, 255])

        mask = cv2.inRange(hsv, lower1, upper1)

        kernel = (3, 3)
        normed = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        kernel = cv2.getStructuringElement(shape=cv2.MORPH_ELLIPSE, ksize=kernel)
        mask = cv2.morphologyEx(normed, cv2.MORPH_OPEN, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        points = []
        # cv2.imshow("mask",mask)
        # print(len(contours))
        for contour in contours:
            # print(cv2.contourArea(contour))
            if cv2.contourArea(contour) > 41:
                # x, y, w, h = cv2.boundingRect(contour)
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1, 16)
                rbox = cv2.minAreaRect(contour)
                (cX, cY), (w, h), rot_angle = rbox
                # print(rot_angle)
                if rot_angle <= 80 and rot_angle >= 100:
                    continue
                points.append((int(cX), int(cY)))
       # if len(points) == 0:
          #  cs = list(map(lambda x: cv2.contourArea(x), contours))
            # cv2.imwrite("low-"+str(uuid.uuid4())+".png", frame)
            # if len(cs) > 0:
            #     print("KEINE DATENPUNKTE!", max(cs))
            # else:
            #     print("KEINE DATENPUNKTE!")
      #  elif len(points) > 2:
            # cv2.imwrite("high-"+str(uuid.uuid4())+".png", frame)
        #    print("MORE THAN 2 POINTS")
            # cv2.imwrite("test.png", frame)
        return points


    @staticmethod
    def get_file_path_for_timestamp(path, timestamp) -> str:
        timestamps = [datetime.datetime.strptime(f, '%Y-%m-%d_%H-%M-%S.mp4')
                      for f in os.listdir(path)
                      if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1] == ".mp4"]
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        timestamps = list(filter(lambda x: x <= timestamp, timestamps))
        if len(timestamps) == 0:
            return None
        file_name = datetime.datetime.strftime(max(timestamps), '%Y-%m-%d_%H-%M-%S.mp4')
        return os.path.join(path, file_name)

    def get_static_positions(self, path, calibration_entities: List[CalibrationEntity]):
        for entity in calibration_entities:
            filePath = Processor.get_file_path_for_timestamp(path, entity.timestamp)
            print("Entity: ", entity)
            cap = cv2.VideoCapture(filePath)
            c_time = os.path.basename(filePath)
            start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
            fps = cap.get(cv2.CAP_PROP_FPS)
            last_time = 0.0
            while cap.isOpened():
                frame_exists, curr_frame = cap.read()
                if frame_exists:

                    frame = curr_frame[510:600, 0:-1]
                    points, mask = self.get_center_of_mass(frame)
                    frame_timestamp = start_time + \
                        datetime.timedelta(milliseconds=last_time)
                    last_time = last_time+1000/fps

                    if str(frame_timestamp) != entity.timestamp:
                        continue
                    else:
                        if len(points) == 1:
                            entity.position2_calculated = points[0][0]
                        elif len(points) == 2:
                            p1 = points[0][0]
                            p2 = points[1][0]
                            if p1 > p2:
                                entity.position1_calculated = p2
                                entity.position2_calculated = p1
                            else:
                                entity.position1_calculated = p1
                                entity.position2_calculated = p2
                        break
                else:
                    break
            cap.release()
            # Closes all the frames
            cv2.destroyAllWindows()

    def analyze(self, filePath: str) -> None:
        fileName = os.path.basename(filePath)
        print("File: ", fileName)
        frameReader = FrameReader(filePath).start()
        c_time = os.path.basename(filePath)
        start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
        fps = frameReader.fps
        # fpsCount = frameReader.fpsCount
        last_time = 0.0
        self.ctx.clearFile(fileName)
        measurements = []
        error_measurements = []
        frameCounter = 0
        while frameReader.more():
            frame = frameReader.read()
            frameCounter += 1
            # if frameCounter % 100 == 0:
            #     print("{}\t{} - {}%".format(datetime.datetime.now().strftime("%H:%M:%S"), fileName, int(frameCounter*10000/fpsCount)/100))
            points = self.get_center_of_mass(frame)
            frame_timestamp = start_time + datetime.timedelta(milliseconds=last_time)
            last_time = last_time+1000/fps
            if len(points) == 2:
                p1 = points[0][0]
                p2 = points[1][0]
                if p1 >= p2:
                    k2Value = p1
                    k1Value = p2
                else:
                    k1Value = p1
                    k2Value = p2
                measurements.append((frame_timestamp, k1Value, k2Value))
            elif len(points) == 1:
                k2Value = points[0][0]
                measurements.append((frame_timestamp, None, k2Value))
            elif len(points) > 2:
                error_measurements.append(frame_timestamp)
        self.ctx.insertMeasurements(fileName, measurements, error_measurements)
        # When everything done, release the video capture object
        # cap.release()
        cv2.destroyAllWindows()
        frameReader.stop()
