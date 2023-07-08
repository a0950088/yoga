import mediapipe as mp
import toolkit
import cv2
import os
import AngleNodeDef
import numpy as np

CWD = os.getcwd().replace("\\","/")
    
class TreePosture():
    # 彎曲腳：右 伸直腳：左
    def __init__(self):
        self.tips = ""
        self.jsonfile_path = f"{CWD}/TreePose/SampleJson/sample_sample1.json"
        self.roi = {
            'LEFT_KNEE': False,
            'LEFT_HIP': False,
            'RIGHT_FOOT_INDEX': False,
            'RIGHT_KNEE': False,
            'RIGHT_HIP': False,
            'LEFT_SHOULDER': False,
            'RIGHT_SHOULDER': False,
            'LEFT_ELBOW': False,
            'RIGHT_ELBOW': False,
            'LEFT_INDEX': False,
            'RIGHT_INDEX': False,
        }
        self.angle_dict = self.initialAngleDict()
        self.sample_angle_dict = {}
    
    def initialAngleDict(self, dict={}):
        index = 0
        for key,_ in AngleNodeDef.TREE_ANGLE.items():
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
        sum_angle = np.zeros(len(AngleNodeDef.TREE_ANGLE))
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Video not open")
            exit()
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Sample Video end")
                break
            _, point3d = toolkit.getMediapipeResult(frame)
            if type(point3d) == int:
                print("sample video detect pose error")
                break
            perFrameOfAngle = []
            for _,value in AngleNodeDef.TREE_ANGLE.items():
                angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                     list(toolkit.getLandmarks(point3d[value[1]])), 
                                     list(toolkit.getLandmarks(point3d[value[2]])))
                perFrameOfAngle.append(angle)
            sum_angle+=perFrameOfAngle
        # print(sum_angle/frame_count) # 平均角度
        sum_angle/=frame_count
        toolkit.writeSampleJsonFile(sum_angle, AngleNodeDef.TREE_ANGLE, storage_path)
        print("Sample Done.")
        cap.release()
    def detect(self, frame, w, h, mode):
        '''
        mode: set mediapipe static_image_mode, True->use to different image/False->use to video
        return draw frame
        '''
        self.tips = ""
        point2d, point3d = toolkit.getMediapipeResult(frame, mode)
        if type(point2d) == int and type(point3d) == int:
            self.tips = "無法偵測到完整骨架"
            return frame
        for key,value in AngleNodeDef.TREE_ANGLE.items():
            angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                    list(toolkit.getLandmarks(point3d[value[1]])), 
                                    list(toolkit.getLandmarks(point3d[value[2]])))
            self.angle_dict[key] = angle
        for key, value in self.roi.items():
            tip_flag = False
            if self.tips == "":
                tip_flag = True
            if key == 'LEFT_KNEE' or key == 'LEFT_HIP':
                tolerance_val = 8
                min_angle = self.sample_angle_dict[key]-tolerance_val
                max_angle = self.sample_angle_dict[key]+tolerance_val
                if self.angle_dict[key]>=min_angle and self.angle_dict[key]<=max_angle:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認左腳重心，避免左腳傾斜造成負擔"
            elif key == 'RIGHT_FOOT_INDEX':
                _,foot_y,_ = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_FOOT_INDEX])
                _,knee_y,_ = toolkit.getLandmarks(point3d[AngleNodeDef.LEFT_KNEE])
                if foot_y <= knee_y:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認右腳腳尖須高於左腳膝蓋，避免造成膝蓋負擔"
            elif key == 'RIGHT_KNEE':
                _,_,knee_z = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
                _,_,hip_z = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
                if self.angle_dict[key]<=60 and ((hip_z-knee_z)*100)<=15:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認右腳膝蓋不可往前傾，須與髖關節保持同一平面"
            elif key == 'RIGHT_HIP':
                if self.angle_dict[key]>=100:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認右腳膝蓋是否正確抬起"
            elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
                if self.angle_dict[key]>=120:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認雙手是否高舉在頭部之上"
            elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
                if self.angle_dict[key]>=90:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認手軸是否盡量往上伸直"
            elif key == 'LEFT_INDEX' or key == 'RIGHT_INDEX':
                index_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.LEFT_INDEX]) if key == 'LEFT_INDEX' else toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_INDEX])
                left_shoulder_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.LEFT_SHOULDER])
                right_shoulder_x,_,_ = toolkit.getLandmarks(point3d[AngleNodeDef.RIGHT_SHOULDER])
                if index_x>=right_shoulder_x and index_x<=left_shoulder_x:
                    self.roi[key] = True
                else:
                    self.roi[key] = False
                    if tip_flag == True:
                        self.tips = "請確認雙手合掌並往上伸直於兩側肩膀中間"
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
            if type(point3d) == int:
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
        if type(point2d) == int and type(point3d) == int:
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
                        self.tips = "請確認右腳膝蓋與腳踝的關節點須重疊，\n並注意大腿下壓的角度"
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
                        self.tips = "請確認兩側肩膀不要過度用力，並將背部挺直，\n盡量將身體面向正面"
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

