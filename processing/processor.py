#!/usr/bin/env python3
import cv2
from ctypes import Array
import numpy as np
import os
import datetime

from db.context import DataContext


class Processor:

    def __init__(self, dataContext: DataContext) -> None:
        self.ctx = dataContext

    def get_center_of_mass(self, frame: Array) -> None:

        # frame = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([160, 40, 105])  # 160,180,40,148,105,219
        upper1 = np.array([180, 148, 219])

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
            # print(cv2.contourArea(contour))
            if cv2.contourArea(contour) > 30:
                # x, y, w, h = cv2.boundingRect(contour)
                # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1, 16)
                rbox = cv2.minAreaRect(contour)
                (cX, cY), (w, h), rot_angle = rbox
                if rot_angle <= 80 and rot_angle >= 100:
                    continue
                points.append((int(cX), int(cY)))
        if len(points) == 0:
            print("KEINE DATENPUNKTE!", max(list(map(lambda x: cv2.contourArea(x), contours))))
        elif len(points) > 2:
            print("MORE THAN 2 POINTS")
        return points

    def analyze(self, filePath: str) -> None:
        fileName = os.path.basename(filePath)
        print("File: ", fileName)
        cap = cv2.VideoCapture(filePath)
        c_time = os.path.basename(filePath)
        start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
        fps = cap.get(cv2.CAP_PROP_FPS)
        last_time = 0.0
        self.ctx.clearFile(fileName)
        while cap.isOpened():
            frame_exists, curr_frame = cap.read()
            if frame_exists:

                frame = curr_frame[510:600, 0:-1]
                points = self.get_center_of_mass(frame)
                frame_timestamp = start_time + \
                    datetime.timedelta(milliseconds=last_time)
                if str(frame_timestamp) == "2022-05-17 16:36:05":
                    break
                last_time = last_time+1000/fps
                m = 1.1373369636
                n = 287.5710922481
                if len(points) == 2:
                    p1 = points[0]
                    p2 = points[1]
                    if p1[0] >= p2[0]:
                        k1Value = int(m*p1[0]+n)
                        k2Value = int(m*p2[0]+n)
                    else:
                        k2Value = int(m*p1[0]+n)
                        k1Value = int(m*p2[0]+n)
                    # self.ctx.insertMeasurement(fileName, frame_timestamp, k1Value, k2Value) #TODO

                    # cv2.putText(frame, str(k1Value), p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1" if p1[0] >= p2[0] else "Kran 2", (p1[0], p1[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, str(k2Value), p2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1" if p2[0] >= p1[0] else "Kran 2", (p2[0], p2[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                elif len(points) == 1:
                    k1Value = int(m*points[0][0]+n)
                    # self.ctx.insertMeasurement(fileName, frame_timestamp, k1Value) # TODO
                    # cv2.putText(frame, str(k1Value), points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    # cv2.putText(frame, "Kran 1", (points[0][0], points[0][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # cv2.imshow('Output', mask)
                # cv2.imshow('frame', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
