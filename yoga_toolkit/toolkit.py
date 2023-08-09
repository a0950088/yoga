import mediapipe as mp
import cv2
import json
import math as m
import yoga_toolkit.AngleNodeDef as AngleNodeDef

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

def treePoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'LEFT_KNEE' or key == 'LEFT_HIP':
            tolerance_val = 8
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            elif angle_dict[key]<min_angle:
                roi[key] = False
                tips = "將左腳打直平均分配雙腳重量，勿將右腳重量全放在左腳大腿" if tip_flag else tips
            else:
                roi[key] = False
                tips = "請勿將右腳重量全放在左腳大腿，避免傾斜造成左腳負擔" if tip_flag else tips
        elif key == 'RIGHT_FOOT_INDEX':
            _,foot_y,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_FOOT_INDEX])
            _,knee_y,_ = getLandmarks(point3d[AngleNodeDef.LEFT_KNEE])
            if foot_y <= knee_y:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請將右腳抬至高於左腳膝蓋的位置，勿將右腳放在左腳膝蓋上，\n避免造成膝蓋負擔"
        elif key == 'RIGHT_KNEE':
            _,_,knee_z = getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
            _,_,hip_z = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if angle_dict[key]<=65 and ((hip_z-knee_z)*100)<=17:
                roi[key] = True
            elif angle_dict[key]>65:
                roi[key] = False
                tips = "請將右腳再抬高一些，不可壓到左腳膝蓋" if tip_flag else tips
            elif ((hip_z-knee_z)*100)>17:
                roi[key] = False
                tips = "將臂部往前推，打開左右骨盆，右腳膝蓋不可向前傾" if tip_flag else tips
            else:
                roi[key] = False
                tips = "右腳膝蓋不可向前傾，須與髖關節保持同一平面" if tip_flag else tips
        elif key == 'RIGHT_HIP':
            if angle_dict[key]>=100:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請確認右腳膝蓋是否已經抬至左腳膝蓋以上" if tip_flag else tips
        elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            if angle_dict[key]>=120:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將雙手合掌並互相施力，往上伸展至頭頂正上方" if tip_flag else tips
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將雙手再往上伸展，使手軸貼近耳朵" if tip_flag else tips
            # if angle_dict[key]>=90:
            #     roi[key] = True
            # else:
            #     roi[key] = False
            #     tips = "請將手再抬高一些，並保持在頭頂正上方" if tip_flag else tips
        elif key == 'LEFT_INDEX' or key == 'RIGHT_INDEX':
            index_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_INDEX]) if key == 'LEFT_INDEX' else getLandmarks(point3d[AngleNodeDef.RIGHT_INDEX])
            left_shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_SHOULDER])
            right_shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_SHOULDER])
            if index_x>=right_shoulder_x and index_x<=left_shoulder_x:
                roi[key] = True
            elif index_x<right_shoulder_x:
                roi[key] = False
                tips = "請將雙手往左移動，保持在頭頂正上方" if tip_flag else tips
            elif index_x>left_shoulder_x:
                roi[key] = False
                tips = "請將雙手往右移動，保持在頭頂正上方" if tip_flag else tips
    if tips == "":
        tips = "動作正確"
    return roi, tips

def warriorIIPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'RIGHT_ANKLE':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將右腳腳尖朝向右手邊，右腳膝蓋往右腳腳踝的方向移動，\n直到小腿與地面呈垂直" if tip_flag else tips
        elif key == 'RIGHT_KNEE':
            ankle_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_ANKLE])
            knee_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
            if angle_dict[key]>=90 and angle_dict[key]<=150 and abs((ankle_x-knee_x)*100)<=10:
                roi[key] = True
            elif abs((ankle_x-knee_x)*100)>10:
                roi[key] = False
                tips = "請將右腳膝蓋往右腳腳踝的方向移動，直到小腿與地面呈垂直" if tip_flag else tips
            elif angle_dict[key]<90:
                roi[key] = False
                tips = "臀部不可低於右腳膝蓋，請將左腳往內收回使臀部高於右腳膝蓋" if tip_flag else tips
            elif angle_dict[key]>150:
                roi[key] = False
                tips = "請將左腳再往後一些，讓臀部有空間可以下壓" if tip_flag else tips
        elif key == 'LEFT_KNEE':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            # if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將左腳膝蓋打直，並將左腳腳尖朝向前方" if tip_flag else tips
        elif key == 'LEFT_HIP' or key == 'RIGHT_HIP':
            if angle_dict[key]>=100:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將雙腳再拉開一些距離，臀部向前推並挺胸" if tip_flag else tips
        elif key == 'NOSE':
            nose_x,_,_ = getLandmarks(point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if nose_x>=(right_hip_x-0.1) and nose_x<=(left_hip_x+0.1):
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將頭轉向彎曲腳的方向並直視前方" if tip_flag else tips
        elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            direction = "右" if key == 'RIGHT_SHOULDER' else "左"
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            elif angle_dict[key]<min_angle:
                roi[key] = False
                tips = f"請將{direction}手抬高，與肩膀呈水平，\n並將身體挺直朝向前方" if tip_flag else tips
            elif angle_dict[key]>max_angle:
                roi[key] = False
                tips = f"請將{direction}手放低，與肩膀呈水平，\n並將身體挺直朝向前方" if tip_flag else tips
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            direction = "右" if key == 'RIGHT_ELBOW' else "左"
            # if angle_dict[key]>=140 and (angle_dict[key]>=min_angle and angle_dict[key]<=max_angle):
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                tips = f"請將{direction}手手心朝下平放並打直{direction}手" if tip_flag else tips
    if tips == "":
        tips = "動作正確"
    return roi, tips

def plankPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    side = 'RIGHT_'
    for key, value in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True

        if key == 'NOSE':
            if point3d[AngleNodeDef.NOSE].x > point3d[AngleNodeDef.LEFT_HIP].x and point3d[AngleNodeDef.NOSE].x > point3d[AngleNodeDef.RIGHT_HIP].x:
                roi['NOSE'] = True
            elif tip_flag == True:
                tips = '請將頭朝向左手邊'
        if key == side + 'EYE':
            eye_shoulder_distance = abs(point3d[AngleNodeDef.RIGHT_SHOULDER].y - point3d[AngleNodeDef.RIGHT_EYE].y)
            forearm_distance = abs(point3d[AngleNodeDef.RIGHT_SHOULDER].y - point3d[AngleNodeDef.RIGHT_ELBOW].y)

            if eye_shoulder_distance >= forearm_distance * 0.05:
                roi['LEFT_EYE'] = True
                roi['RIGHT_EYE'] = True
            elif tip_flag == True:
                tips = "請將頭抬起，保持頸椎平行於地面"

        elif key == side + 'ELBOW':
            elbow_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_ELBOW])
            shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_SHOULDER])
            hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if abs(elbow_x - shoulder_x) < abs(hip_x - shoulder_x) * 0.1:
                roi['RIGHT_ELBOW'] = True
                roi['LEFT_ELBOW'] = True
            elif tip_flag == True:
                roi['RIGHT_ELBOW'] = False
                roi['LEFT_ELBOW'] = False
                if elbow_x > shoulder_x:
                    tips = "請將手肘向後縮並確認手肘位置在肩關節下方"
                else:
                    tips = "請將手肘向前移並確認手肘位置在肩關節下方"

        elif key == side + 'SHOULDER':
            tolerance_val = 10
            min_angle = sample_angle_dict['RIGHT_SHOULDER']-tolerance_val
            max_angle = sample_angle_dict['RIGHT_SHOULDER']+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi['RIGHT_SHOULDER'] = True
                roi['LEFT_SHOULDER'] = True
            elif tip_flag == True:
                roi['RIGHT_SHOULDER'] = False
                roi['LEFT_SHOULDER'] = False
                if angle_dict[key] < min_angle:
                    tips = "請將手肘向前移並維持頸椎、胸椎、腰椎維持一直線平行於地面"
                else:
                    tips = "請將手肘向後縮並維持頸椎、胸椎、腰椎維持一直線平行於地面"

        elif key == side + 'HIP':
            tolerance_val = 10
            min_angle = sample_angle_dict['RIGHT_HIP']-tolerance_val
            max_angle = sample_angle_dict['RIGHT_HIP']+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi['RIGHT_HIP'] = True
                roi['LEFT_HIP'] = True
            elif angle_dict[key] < min_angle and tip_flag == True:
                roi['RIGHT_HIP'] = False
                roi['LEFT_HIP'] = False
                tips = "請將屁股稍微放下"
            elif tip_flag == True:
                roi['RIGHT_HIP'] = False
                roi['LEFT_HIP'] = False
                tips = "請將屁股稍微抬起"

        elif key == side + 'KNEE':
            tolerance_val = 10
            min_angle = sample_angle_dict['RIGHT_KNEE']-tolerance_val
            max_angle = sample_angle_dict['RIGHT_KNEE']+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi['RIGHT_KNEE'] = True
                roi['LEFT_KNEE'] = True
            elif tip_flag == True:
                roi['RIGHT_KNEE'] = False
                roi['LEFT_KNEE'] = False
                tips = "請將膝蓋伸直並讓腳踝到膝蓋成一直線"

        elif key == side + 'ANKLE':
            tolerance_val = 15
            min_angle = 30
            if angle_dict[key]>=min_angle:
                roi['RIGHT_ANKLE'] = True
                roi['LEFT_ANKLE'] = True
            elif angle_dict[key] < min_angle and tip_flag == True:
                print(angle_dict[key], min_angle)
                roi['RIGHT_ANKLE'] = False
                roi['LEFT_ANKLE'] = False
                tips = "請用前腳掌將身體撐起"

    if tips == "":
        tips = "動作正確"
    return roi, tips
    
def reversePlankPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    side = ""
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'NOSE':
            node_x,_,_ = getLandmarks(point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if node_x>left_hip_x and node_x>right_hip_x:
                roi[key] = True
                side = "LEFT"
            elif node_x<left_hip_x and node_x<right_hip_x:
                roi[key] = True
                side = "RIGHT"
            else:
                roi[key] = False
                tips = "請將身體面向右方或左方坐下，並將雙手撐在肩膀下方，\n使上半身呈現斜線" if tip_flag else tips
                break
        if key == f"{side}_ELBOW":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            # min_angle = sample_angle_dict[f"{sample_side}_ELBOW"]-tolerance_val
            # max_angle = sample_angle_dict[f"{sample_side}_ELBOW"]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請將雙手手軸打直" if tip_flag else tips
        elif key == f"{side}_INDEX":
            index_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_INDEX])
            shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_SHOULDER])
            if side == "LEFT":
                index_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_INDEX])
                shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_SHOULDER])
            if index_x < shoulder_x and side == "LEFT":
                roi["LEFT_INDEX"] = True
                roi["RIGHT_INDEX"] = True
            elif index_x > shoulder_x and side == "RIGHT":
                roi["LEFT_INDEX"] = True
                roi["RIGHT_INDEX"] = True
            else:
                roi["LEFT_INDEX"] = False
                roi["RIGHT_INDEX"] = False
                tips = "請將雙手手指朝向臀部，並將手臂打直，垂直於地面" if tip_flag else tips
        elif key == f"{side}_WRIST":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            # min_angle = sample_angle_dict[f"{sample_side}_WRIST"]-tolerance_val
            # max_angle = sample_angle_dict[f"{sample_side}_WRIST"]+tolerance_val
            # if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
            if angle_dict[key]<=max_angle:
                roi["LEFT_WRIST"] = True
                roi["RIGHT_WRIST"] = True
            else:
                roi["LEFT_WRIST"] = False
                roi["RIGHT_WRIST"] = False
                tips = "請將手掌平貼於地面，\n讓肩膀、手軸、手腕成一直線垂直於地面" if tip_flag else tips
        elif key == f"{side}_SHOULDER":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            # min_angle = sample_angle_dict[f"{sample_side}_SHOULDER"]-tolerance_val
            # max_angle = sample_angle_dict[f"{sample_side}_SHOULDER"]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "將臀部抬起，胸往前挺，使脊椎保持一直線" if tip_flag else tips
        elif key == f"{side}_HIP":
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            # min_angle = sample_angle_dict[f"{sample_side}_HIP"]-tolerance_val
            # max_angle = sample_angle_dict[f"{sample_side}_HIP"]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請將臀部抬高一些，使身體保持一直線" if tip_flag else tips
        elif key == f"{side}_KNEE":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            # min_angle = sample_angle_dict[f"{sample_side}_KNEE"]-tolerance_val
            # max_angle = sample_angle_dict[f"{sample_side}_KNEE"]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請將雙腳膝蓋打直，使身體保持一直線" if tip_flag else tips
    if tips == "":
        tips = "動作正確"
    return roi, tips