import mediapipe as mp
import cv2
import json
import math as m

mp_pose = mp.solutions.pose
pose_connection = mp_pose.POSE_CONNECTIONS
nodeList = mp.solutions.pose.PoseLandmark
mp_sample_pose = mp_pose.Pose(static_image_mode=True,
                                        model_complexity=2,
                                        min_detection_confidence=0.5)
mp_result_pose = mp_pose.Pose(static_image_mode=False,
                                        model_complexity=2,
                                        min_detection_confidence=0.5)

def getMediapipeResult(frame, mode=True):
    try:
        if mode:
            results = mp_sample_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            results = mp_result_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        point2d = results.pose_landmarks.landmark
        point3d = results.pose_world_landmarks.landmark
        return point2d, point3d
    except:
        return 0, 0

def getLandmarks(landmark, w=None, h=None):
    '''
    Get landmark x,y,z respectively
    '''
    if w == None or h == None:
        return landmark.x, landmark.y, landmark.z
    else:
        return int(landmark.x*w), int(landmark.y*h)

def readSampleJsonFile(path):
    try:
        with open(path, 'r') as file:
            sample_angle = json.load(file)
            return sample_angle
    except:
        return None

def writeSampleJsonFile(angle_array, angle_def, path):
    data = {}
    index = 0
    for key,_ in angle_def.items():
        data[key] = angle_array[index]
        index+=1
    print(data)
    with open(path, 'w') as file:
        json.dump(data, file)

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