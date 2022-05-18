#!/usr/bin/env python3
import cv2
from ctypes import Array
import numpy as np
import os
import datetime


class Processor:

    def get_center_of_mass(self, frame: Array) -> None:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([169, 150, 20])
        upper1 = np.array([180, 255, 255])

        mask = cv2.inRange(hsv, lower1, upper1)

        # lower2 = np.array([0, 120, 20])
        # upper2 = np.array([12, 255, 255])

        # mask2 = cv2.inRange(hsv, lower2, upper2)

        # mask = cv2.bitwise_or(mask1, mask2)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        points = []
        if len(contours) != 0:
            for contour in contours:
                if cv2.contourArea(contour) > 20:
                    x, y, w, h = cv2.boundingRect(contour)
                    # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 1)
                    cX = int(x+w/2)
                    cY = int(y+h/2)
                    points.append((cX, cY))
                    cv2.circle(frame, (cX, cY), 30, [255, 255, 255])
                    # print(cX,cY)
                    # cv2.putText(frame, "center", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.imshow('Output', mask)
        return points

    def analyze(self, filePath: str, timestamp: str) -> None:
        cap = cv2.VideoCapture(filePath)
        c_time = os.path.basename(filePath)
        start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
        print(start_time)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        print("width",width)
        last_time = 0.0
        while cap.isOpened():
            # Capture frame-by-frame
            frame_exists, curr_frame = cap.read()
            if frame_exists:
                frame = curr_frame[510:600, 0:-1]
                points = self.get_center_of_mass(frame)
                frame_timestamp = start_time + \
                    datetime.timedelta(milliseconds=last_time)
                last_time = last_time+1000/fps
                m = 1.137195078
                n = 390.392018851
                if len(points) == 1:
                    cv2.putText(frame, str(m*points[0][0]+n), points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.imshow('frame', frame)
                    # return
                # Display the resulting frame
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
