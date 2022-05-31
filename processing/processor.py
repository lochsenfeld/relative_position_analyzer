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


class Processor:

    def __init__(self, dataContext: DataContext) -> None:
        self.ctx = dataContext

    def get_center_of_mass(self, frame: Array) -> None:

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # h_low = cv2.getTrackbarPos("h_low", "trackbars")
        # h_high = cv2.getTrackbarPos("h_high", "trackbars")
        # s_low = cv2.getTrackbarPos("s_low", "trackbars")
        # s_high = cv2.getTrackbarPos("s_high", "trackbars")
        # v_low = cv2.getTrackbarPos("v_low", "trackbars")
        # v_high = cv2.getTrackbarPos("v_high", "trackbars")

        lower1 = np.array([160, 57, 105])
        upper1 = np.array([180, 148, 219])
        # lower1 = np.array([h_low, s_low, v_low])
        # upper1 = np.array([h_high, s_high, v_high])

        mask1 = cv2.inRange(hsv, lower1, upper1)

        lower2 = np.array([169, 150, 20])
        upper2 = np.array([180, 255, 255])

        mask2 = cv2.inRange(hsv, lower2, upper2)

        mask = cv2.bitwise_or(mask1, mask2)

        lower3 = np.array([172, 0, 136])
        upper3 = np.array([173, 41, 144])
        mask3 = cv2.inRange(hsv, lower3, upper3)

        mask = cv2.subtract(mask, mask3)

        lower4 = np.array([173, 40, 101])
        upper4 = np.array([178, 52, 127])
        mask4 = cv2.inRange(hsv, lower4, upper4)

        mask = cv2.subtract(mask, mask4)

        kernel = (3, 3)
        # mask = cv2.erode(mask, kernel, iterations=cv2.getTrackbarPos("i1", "trackbars"))
        # mask = cv2.dilate(mask, kernel, iterations=cv2.getTrackbarPos("i2", "trackbars"))
        normed = cv2.normalize(mask, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
        kernel = cv2.getStructuringElement(shape=cv2.MORPH_ELLIPSE, ksize=(3, 3))
        mask = cv2.morphologyEx(normed, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        points = []

        for contour in contours:
            if cv2.contourArea(contour) > 20:
                # x, y, w, h = cv2.boundingRect(contour)
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1, 16)
                rbox = cv2.minAreaRect(contour)
                (cX, cY), (w, h), rot_angle = rbox
                if rot_angle <= 80 and rot_angle >= 100:
                    continue
                points.append((int(cX), int(cY)))
        if len(points) == 0:
            cs = list(map(lambda x: cv2.contourArea(x), contours))
            if len(cs) > 0:
                print("KEINE DATENPUNKTE!", max(cs))
            else:
                print("KEINE DATENPUNKTE!")
        elif len(points) > 2:
            print("MORE THAN 2 POINTS")
            # cv2.imwrite("test.png", frame)
        return points, mask

    def test(self):

        # c2 = cv2.VideoCapture("D:/Projekte/macki/Kalibrierung 17.05/Kranstellungen 17.05/2022-05-17_22-59-41.mp4")
        # _, f2 = c2.read()
        # f2 = f2[510:600, 0:-1]
        cv2.namedWindow("trackbars")
        cv2.resizeWindow("trackbars", 1900, 200)

        def empty(x):
            pass
        # 160,180,40,148,105,219

        # lower1 = np.array([160, 40, 105])
        # upper1 = np.array([180, 148, 219])
        cv2.createTrackbar("h_low", "trackbars", 160, 180, empty)
        cv2.createTrackbar("h_high", "trackbars", 180, 180, empty)
        cv2.createTrackbar("s_low", "trackbars", 40, 255, empty)
        cv2.createTrackbar("s_high", "trackbars", 148, 255, empty)
        cv2.createTrackbar("v_low", "trackbars", 105, 255, empty)
        cv2.createTrackbar("v_high", "trackbars", 219, 255, empty)
        cv2.createTrackbar("i1", "trackbars", 3, 10, empty)
        cv2.createTrackbar("i2", "trackbars", 4, 10, empty)
        while True:
            f1 = cv2.imread("test.png")
            m1 = self.get_center_of_mass(f1)
            cv2.imshow('f1', f1)
            cv2.imshow('m1', m1)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        # Closes all the frames
        cv2.destroyAllWindows()

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
            fileName = os.path.basename(filePath)
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
        cap = cv2.VideoCapture(filePath)
        c_time = os.path.basename(filePath)
        start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        last_time = 0.0
        self.ctx.clearFile(fileName)
        start = time.time()
        measurements = []
        while cap.isOpened():
            frame_exists, curr_frame = cap.read()
            if frame_exists:

                frame = curr_frame[510:600, 0:-1]
                points, mask = self.get_center_of_mass(frame)
                frame_timestamp = start_time + \
                    datetime.timedelta(milliseconds=last_time)
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
                    # cv2.putText(frame, str(k1Value), p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1" if p1[0] >= p2[0] else "Kran 2", (p1[0], p1[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, str(k2Value), p2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1" if p2[0] >= p1[0] else "Kran 2", (p2[0], p2[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                elif len(points) == 1:
                    k2Value = points[0][0]
                    measurements.append((frame_timestamp, None, k2Value))
                    # cv2.putText(frame, str(k1Value), points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1", (points[0][0], points[0][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # cv2.imshow('Output', mask)
                # cv2.imshow('frame', frame)
                # if cv2.waitKey(25) & 0xFF == ord('q'):
                #     break

            # Break the loop
            else:
                break
        self.ctx.insertMeasurements(fileName, measurements)
        end = time.time()
        print("Took x seconds:", int(end - start))
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
