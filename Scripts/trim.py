import cv2
import mediapipe as mp
import sys
import os
from tqdm import tqdm
from time import sleep

# python trim.py videopath secondsoffstart secondsoffend
# pyton trim.py /test.mp4 3 15
def main():
    if not os.path.exists(sys.argv[1]):
        print("Path does not exist")
    elif sys.argv[2] == None or sys.argv[3] == None:
        print("Need seconds off start and end")
    else:
        fps, start, end = 30, int(sys.argv[2]), int(sys.argv[3])
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter("output.mp4", fourcc, fps, (1920, 1080))
        cap = cv2.VideoCapture(sys.argv[1])

        for _ in tqdm(range(start), desc="Processing"):
            working, img = cap.read()
            if not working:
                break
        
        for _ in tqdm(range(start*fps,int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-end*fps), desc="Processing"):
            working, img = cap.read()
            if not working:
                break
            video.write(img)

        cap.release()
        video and video.release()

if __name__ == "__main__":
    main()