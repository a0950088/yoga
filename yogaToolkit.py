import cv2
import mediapipe as mp
import numpy as np
import math as m
import AngleNodeDef
from statistics import median
import json


mp_drawing = mp.solutions.drawing_utils # mediapipe 繪圖方法
mp_drawing_styles = mp.solutions.drawing_styles # mediapipe 繪圖樣式
mp_holistic = mp.solutions.holistic # mediapipe 全身偵測方法
def computeAngle(point1, centerPoint, point2):
    p1_x, pc_x, p2_x = point1[0], centerPoint[0], point2[0]
    p1_y, pc_y, p2_y = point1[1], centerPoint[1], point2[1] 

    if len(point1) == len(centerPoint) == len(point2) == 3:
        # 3 dim
        p1_z, pc_z, p2_z = point1[2], centerPoint[2], point2[2]
    else:
        # 2 dim
        p1_z, pc_z, p2_z = 0,0,0

    # vector
    x1,y1,z1 = (p1_x-pc_x),(p1_y-pc_y),(p1_z-pc_z)
    x2,y2,z2 = (p2_x-pc_x),(p2_y-pc_y),(p2_z-pc_z)

    # angle
    cos_b = (x1*x2 + y1*y2 + z1*z2) / (m.sqrt(x1**2 + y1**2 + z1**2) *(m.sqrt(x2**2 + y2**2 + z2**2)))
    B = m.degrees(m.acos(cos_b))
    return B

def getPointList(w, h, point1, point2, point3):
    p1 = [point1.x*w, point1.y*h, point1.z]
    p2 = [point2.x*w, point2.y*h, point2.z]
    p3 = [point3.x*w, point3.y*h, point3.z]
    return p1,p2,p3

def readSampleJsonFile(path):
    with open(path, 'r') as file:
        sample_angle = json.load(file)
        return sample_angle

def sampleVideo(videoPath, storagePath):
    sampleOffset = 8
    cap = cv2.VideoCapture(videoPath)

    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        refine_face_landmarks=True) as holistic:
        if not cap.isOpened():
            print("Video not open")
            exit()
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(original_width, original_height)
        allCorrectAngle = []
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video end")
                break
            results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            poseLandmarks = results.pose_landmarks.landmark
            nodeList = mp.solutions.holistic.PoseLandmark
            
            perFrameOfAngle = []
            for anglePoint in AngleNodeDef.ALL_ANGLE_POINTS:
                point1, pointCenter, point2 = getPointList(original_width,
                                                            original_height,
                                                            poseLandmarks[nodeList(AngleNodeDef.ALL_ANGLE_POINTS[anglePoint][0])], 
                                                            poseLandmarks[nodeList(AngleNodeDef.ALL_ANGLE_POINTS[anglePoint][1])], 
                                                            poseLandmarks[nodeList(AngleNodeDef.ALL_ANGLE_POINTS[anglePoint][2])])
                angle = computeAngle(point1, pointCenter, point2)
                perFrameOfAngle.append(angle)
                print("Angle: ", round(angle,2))
                point1 = [int(i) for i in point1]
                pointCenter = [int(i) for i in pointCenter]
                point2 = [int(i) for i in point2]
            allCorrectAngle.append(perFrameOfAngle)
        allCorrectAngle = np.array(allCorrectAngle)
        allCorrectAngle = allCorrectAngle.T
        output_dict = {}
        index = 0
        for key in AngleNodeDef.ALL_ANGLE_POINTS:
            median_angle = median(allCorrectAngle[index])
            print(median_angle)
            temp = [median_angle-sampleOffset,median_angle+sampleOffset]
            output_dict[key] = temp
            temp = []
            index+=1
        print(output_dict)
        with open(f"{storagePath}/sample2.json", 'w') as file:
            json.dump(output_dict, file)
    cap.release()
    # output.release()
    cv2.destroyAllWindows()
    
def detectVideo(detectPath, storagePath, sampleAngle):
    cap = cv2.VideoCapture(detectPath)

    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        refine_face_landmarks=True) as holistic:
        if not cap.isOpened():
            print("Video not open")
            exit()
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(original_width, original_height)
        output = cv2.VideoWriter(storagePath, cv2.VideoWriter_fourcc(*'mp4v'), fps, (original_width, original_height))
        # output = cv2.VideoWriter('Warrior2_style3_test_demo.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (original_width, original_height))
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Video end")
                break
            results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # print(results.pose_landmarks == None) 不知道為什麼會有None的情況
            poseLandmarks = results.pose_landmarks.landmark
            nodeList = mp.solutions.holistic.PoseLandmark
            
            for key,value in AngleNodeDef.ALL_ANGLE_POINTS.items():
                point1, pointCenter, point2 = getPointList(original_width,
                                                            original_height,
                                                            poseLandmarks[nodeList(value[0])], 
                                                            poseLandmarks[nodeList(value[1])], 
                                                            poseLandmarks[nodeList(value[2])])
                angle = computeAngle(point1, pointCenter, point2)
                min_sample_angle = sampleAngle[key][0]
                max_sample_angle = sampleAngle[key][1]
                    
                # print("Angle: ", round(angle,2))
                point1 = [int(i) for i in point1]
                pointCenter = [int(i) for i in pointCenter]
                point2 = [int(i) for i in point2]
                # text = f"{round(angle,2)} deg"
                text = f"{int(angle)} deg"
                if(angle>=min_sample_angle and angle<=max_sample_angle):
                    cv2.putText(frame, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # cv2.putText(frame, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.line(frame, point1[:2], pointCenter[:2], (0, 255, 255), 1)
                cv2.line(frame, point2[:2], pointCenter[:2], (0, 255, 255), 1)
                cv2.circle(frame, point1[:2], 3, (255, 0, 0), -1)
                cv2.circle(frame, pointCenter[:2], 3, (255, 0, 0), -1)
                cv2.circle(frame, point2[:2], 3, (255, 0, 0), -1)
            cv2.imshow("Video", frame)
            output.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    output.release()
    cv2.destroyAllWindows()
    
def detectImage(imagePath, storagePath, sampleAngle):
    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        refine_face_landmarks=True) as holistic:
        for idx, file in enumerate(imagePath):
            #cv2 image width是y軸 height是x軸
            image = cv2.imread(file)
            image_height, image_width, _ = image.shape # height width channel
            print(image.shape)
            # Convert the BGR image to RGB before processing.
            results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            poseLandmarks = results.pose_landmarks.landmark
            nodeList = mp.solutions.holistic.PoseLandmark
            
            for key,value in AngleNodeDef.ALL_ANGLE_POINTS.items():
                point1, pointCenter, point2 = getPointList(image_width,
                                                            image_height,
                                                            poseLandmarks[nodeList(value[0])], 
                                                            poseLandmarks[nodeList(value[1])], 
                                                            poseLandmarks[nodeList(value[2])])
                angle = computeAngle(point1, pointCenter, point2)
                min_sample_angle = sampleAngle[key][0]
                max_sample_angle = sampleAngle[key][1]
                    
                # print("Angle: ", round(angle,2))
                point1 = [int(i) for i in point1]
                pointCenter = [int(i) for i in pointCenter]
                point2 = [int(i) for i in point2]
                # text = f"{round(angle,2)} deg"
                text = f"{int(angle)} deg"
                if(angle>=min_sample_angle and angle<=max_sample_angle):
                    cv2.putText(image, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.putText(image, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # cv2.putText(frame, text, pointCenter[:2], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.line(image, point1[:2], pointCenter[:2], (0, 255, 255), 1)
                cv2.line(image, point2[:2], pointCenter[:2], (0, 255, 255), 1)
                cv2.circle(image, point1[:2], 3, (255, 0, 0), -1)
                cv2.circle(image, pointCenter[:2], 3, (255, 0, 0), -1)
                cv2.circle(image, point2[:2], 3, (255, 0, 0), -1)
            print("--------------")
            f"{storagePath}/{str(idx)}.jpg"
            cv2.imwrite(f"{storagePath}/{str(idx)}.jpg", image)
            cv2.imshow("image", image)
            cv2.waitKey(0)