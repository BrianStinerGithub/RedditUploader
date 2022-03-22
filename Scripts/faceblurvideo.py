from genericpath import exists
import cv2
import mediapipe as mp
import sys
import os
from tqdm import tqdm
from time import sleep

class FaceDetector():
    def __init__(self, minDetectionCon = 0.5):
        self.minDetectionCon = minDetectionCon
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(minDetectionCon)
    
    def findFaces(self, image):
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.faceDetection.process(imageRGB)
        bboxes = []
        if self.results.detections is not None:
            for id, detection in enumerate(self.results.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = image.shape
                bbox = int(abs(bboxC.xmin) * iw), int(abs(bboxC.ymin) * ih), int(abs(bboxC.width) * iw), int(abs(bboxC.height) * ih)
                bboxes.append(bbox)
        return image, bboxes
    
    def blurFaces(self, image):
        img, bboxes = self.findFaces(image)
        for bbox in bboxes:
            x, y, w, h = bbox
            face = img[y:y + h, x:x + w]
            blurredface = cv2.blur(face, (75, 75), cv2.BORDER_DEFAULT)
            img[y:y + h, x:x + w] = blurredface         
        return img
    
    def cropFaces(self, image):
        img, bboxes = self.findFaces(image)
        for bbox in bboxes:
            x, y, w, h = bbox
            half_face_y = int(y + h/2)
            leftx, rightx = int(half_face_y*16/9), int(img.shape[1] - half_face_y*16/9)
            img = img[half_face_y:img.shape[0], leftx:rightx]
        return img

def main():
    if not os.path.exists(sys.argv[1]):
        print("Path does not exist")
    else:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter("output.mp4", fourcc, 30, (1920, 1080))
        cap = cv2.VideoCapture(sys.argv[1])
        detector = FaceDetector()

        for _ in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))), desc="Processing"):
            working, img = cap.read()
            if not working:
                break
            image = detector.cropFaces(img)
            video.write(image)
            

        cap.release()
        video and video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
