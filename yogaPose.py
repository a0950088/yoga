import mediapipe as mp
import toolkit
import cv2
import os
import AngleNodeDef
import numpy as np

CWD = os.getcwd().replace("\\","/")
    
class TreePosture():
    def __init__(self):
        pass

class WarriorIIPosture():
    # 彎曲腳：右 伸直腳：左
    def __init__(self):
        self.tips = ""
        self.jsonfile_path = f"{CWD}/WarriorTwoPose/SampleJson/sample_Warrior2_Pose3_Trim.json"
        self.frame, self.results = None, None
        self.roi = {
            'RIGHT_ANKLE': False,
            'RIGHT_KNEE': False,
            'LEFT_KNEE': False,
            'LEFT_HIP': False,
            'RIGHT_HIP': False,
            'NOSE': False,
            'LEFT_SHOULDER': False,
            'RIGHT_SHOULDER': False,
            'LEFT_ELBOW': False,
            'RIGHT_ELBOW': False
        }
        self.angle_dict = self.initialAngleDict()
        self.sample_angle_dict = {}
    
    def initialAngleDict(self, dict={}):
        index = 0
        for key,_ in AngleNodeDef.WARRIOR_II_ANGLE.items():
            dict[key] = 0
            index+=1
        return dict
    
    def initialDetect(self):
        self.sample_angle_dict = toolkit.readSampleJsonFile(self.jsonfile_path)
        if self.sample_angle_dict == None:
            return False
        else:
            return True
    
    def sample(self, video_path, storage_path):
        '''
        看之後這功能要不要拉出來
        Sample angle and storage to json
        return: None
        '''
        print(f"Sampling {video_path}...")
        sum_angle = np.zeros(len(AngleNodeDef.WARRIOR_II_ANGLE))
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Video not open")
            exit()
            
        # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Sample Video end")
                break
            _, point3d = toolkit.getMediapipeResult(frame)
            if point3d == None:
                print("sample video detect pose error")
                exit()
            perFrameOfAngle = []
            for _,value in AngleNodeDef.WARRIOR_II_ANGLE.items():
                angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                     list(toolkit.getLandmarks(point3d[value[1]])), 
                                     list(toolkit.getLandmarks(point3d[value[2]])))
                perFrameOfAngle.append(angle)
            sum_angle+=perFrameOfAngle
        # print(sum_angle/frame_count) # 平均角度
        sum_angle/=frame_count
        toolkit.writeSampleJsonFile(sum_angle, AngleNodeDef.WARRIOR_II_ANGLE, storage_path)
        print("Sample Done.")
        cap.release()
        
    def detect(self, frame, w, h, mode):
        '''
        mode: set mediapipe static_image_mode, True->use to different image/False->use to video
        return draw frame
        '''
        self.tips = ""
        point2d, point3d = toolkit.getMediapipeResult(frame, mode)
        if point2d == None and point3d == None:
            self.tips = "無法偵測到完整骨架"
            return frame
        for key,value in AngleNodeDef.WARRIOR_II_ANGLE.items():
            angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                    list(toolkit.getLandmarks(point3d[value[1]])), 
                                    list(toolkit.getLandmarks(point3d[value[2]])))
            self.angle_dict[key] = angle
        for key, value in self.roi.items():
            tip_flag = False
            if self.tips == "":
                tip_flag = True
            if key == 'RIGHT_ANKLE':
                tolerance_val = 5
                min_angle = self.sample_angle_dict[key]-tolerance_val
                max_angle = self.sample_angle_dict[key]+tolerance_val
                if self.angle_dict[key]>=min_angle and self.angle_dict[key]<=max_angle:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認右腳腳尖須朝向墊子右方"
            elif key == 'RIGHT_KNEE':
                ankle_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_ANKLE])
                knee_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
                if self.angle_dict[key]>=90 and self.angle_dict[key]<=150 and abs((ankle_x-knee_x)*100)<=10:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認右腳膝蓋與腳踝的關節點須重疊，並注意大腿下壓的角度"
            elif key == 'LEFT_KNEE':
                tolerance_val = 10
                min_angle = self.sample_angle_dict[key]-tolerance_val
                max_angle = self.sample_angle_dict[key]+tolerance_val
                if self.angle_dict[key]>=min_angle and self.angle_dict[key]<=max_angle:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認左腳需盡量伸直，且左腳腳尖需朝向墊子前方"
            elif key == 'LEFT_HIP' or key == 'RIGHT_HIP':
                if self.angle_dict[key]>=100:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認兩側骨盆向外打開並挺胸"
            elif key == 'NOSE':
                nose_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.NOSE])
                left_hip_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.LEFT_HIP])
                right_hip_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
                if nose_x>=(right_hip_x-0.1) and nose_x<=(left_hip_x+0.1):
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認頭部位於骨盆正上方，且將頭轉向彎曲腳的方向"
            elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
                tolerance_val = 5
                min_angle = self.sample_angle_dict[key]-tolerance_val
                max_angle = self.sample_angle_dict[key]+tolerance_val
                if self.angle_dict[key]>=min_angle and self.angle_dict[key]<=max_angle:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認兩側肩膀不要過度用力，並將背部挺直，盡量將身體面向正面"
            elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
                tolerance_val = 5
                min_angle = self.sample_angle_dict[key]-tolerance_val
                max_angle = self.sample_angle_dict[key]+tolerance_val
                if self.angle_dict[key]>=140 and (self.angle_dict[key]>=min_angle and self.angle_dict[key]<=max_angle):
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認雙手是否平舉並伸向墊子兩側"
        if self.tips == "":
            self.tips = "動作正確 ! "
        return self.draw(w, h, frame, point2d)
    
    def draw(self, w, h, frame, point2d):
        # draw body connection
        for m in toolkit.pose_connection:
            cv2.line(frame, toolkit.getLandmarks(point2d[m[0]], w, h), list(toolkit.getLandmarks(point2d[m[1]], w, h)), (0, 255, 255), 1)
        # draw points
        point_color = (0,0,0)
        for node in toolkit.nodeList:
            if node.name in self.roi:
                if self.roi[node.name]:
                    point_color = (0,255,0)
                else:
                    point_color = (0,0,255)
            else:
                point_color = (255,255,255)
            cv2.circle(frame, toolkit.getLandmarks(point2d[node.value], w, h), 3, point_color, -1)
        return frame

class PlankPosture():
    def __init__(self):
        pass

class ReversePlankPosture():
    def __init__(self):
        pass

# IMAGE_FILES = ['./WarriorTwoPose/Image/detect/test1.jpg',
#                './WarriorTwoPose/Image/detect/f1.jpg']
# # sample video path
# sample_path = f"{CWD}/WarriorTwoPose/Video/sample/Warrior2_Pose3_Trim.mp4"
# file_name = (sample_path.split('/')[-1]).split('.')[0]
# storage_path = f"{CWD}/WarriorTwoPose/SampleJson/sample_{file_name}.json"

# # detect video path
# video_path = f"{CWD}/WarriorTwoPose/Video/detect/test3.mp4"

# warriorII = WarriorIIPosture()
# warriorII.sample(sample_path, storage_path)
# # for idx, file in enumerate(IMAGE_FILES):
# #     image = cv2.imread(file)
# #     image_height, image_width, _ = image.shape
# #     frame = warriorII.detect(image, image_width, image_height)
# #     cv2.imshow('image',frame)
# #     cv2.waitKey(0)
# if not warriorII.initialDetect():
#     print("Please check sample file exist, or run sample function.")
#     exit()
    
# cap = cv2.VideoCapture(video_path)
# original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# print(original_width,original_height)
# fps = cap.get(cv2.CAP_PROP_FPS)
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Video end")
#         break
#     frame = warriorII.detect(frame, original_width, original_height)
#     print(warriorII.tips)
#     cv2.imshow('image',frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()