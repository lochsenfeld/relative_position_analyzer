#!/usr/bin/env python3
import cv2
from ctypes import Array
import numpy as np
import os
import datetime
import time


class Processor:

    def get_center_of_mass(self, frame: Array) -> None:
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower1 = np.array([169, 150, 20])
        upper1 = np.array([180, 255, 255])

        mask = cv2.inRange(hsv, lower1, upper1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        points = []
        if len(contours) != 0:
            for contour in contours:
                if cv2.contourArea(contour) > 20:
                    #print(cv2.contourArea(contour))
                    x, y, w, h = cv2.boundingRect(contour)
                    cX = int(x+w/2)
                    cY = int(y+h/2)
                    points.append((cX, cY))
                    cv2.circle(frame, (cX, cY), 30, [255, 255, 255])
        cv2.imshow('Output', mask)
        return points

    def analyze(self, filePath: str, timestamp: str) -> None:
        cap = cv2.VideoCapture(filePath)
        c_time = os.path.basename(filePath)
        start_time = datetime.datetime.strptime(c_time, '%Y-%m-%d_%H-%M-%S.mp4')
        print(start_time)
        fps = cap.get(cv2.CAP_PROP_FPS)
        last_time = 0.0
        prev_frame_time = 0
        new_frame_time = 0
        while cap.isOpened():
            # Capture frame-by-frame
            frame_exists, curr_frame = cap.read()
            if frame_exists:
                new_frame_time = time.time()
                fps2 = 1/(new_frame_time-prev_frame_time)
                prev_frame_time = new_frame_time
                fps2 = str(int(fps2))
              
                frame = curr_frame[510:600, 0:-1]
                cv2.putText(frame, fps2, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)
                points = self.get_center_of_mass(frame)
                frame_timestamp = start_time + \
                    datetime.timedelta(milliseconds=last_time)
                last_time = last_time+1000/fps
                m = 1.1373369636
                n = 287.5710922481
                if len(points) == 2:
                    p1 = points[0]
                    p2 = points[1]
                    cv2.putText(frame, str(m*p1[0]+n), p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, "Kran 1" if p1[0] >= p2[0] else "Kran 2", (p1[0], p1[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, str(m*p2[0]+n), p2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, "Kran 1" if p2[0] >= p1[0] else "Kran 2", (p2[0], p2[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                elif len(points) == 1:
                    cv2.putText(frame, str(m*points[0][0]+n), points[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, "Kran 1", (points[0][0], points[0][1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                elif len(points) > 2:
                    print("more than 2 points")
                cv2.imshow('frame', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
