import yoga_toolkit.toolkit as toolkit
import cv2
import yoga_toolkit.AngleNodeDef as AngleNodeDef
import numpy as np

class YogaPose():
    '''
    type: WarriorII, Tree, ReversePlank, Plank ...etc
    '''
    def __init__(self, type):
        self.type = type
        self.tips = ""
        self.roi, self.angle_def, self.jsonfile_path, self.samplefile_path = self.initialize(type)
        self.angle_dict = self.initialAngleDict()
        self.sample_angle_dict = {}
        
    def initialize(self, type):
        roi = {}
        angle_def = None
        jsonfile_path = ""
        samplefile_path = ""
        if type == 'Tree':
            roi = {
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
            angle_def = AngleNodeDef.TREE_ANGLE
            jsonfile_path = f"yoga_toolkit/JsonFile/TreePose/sample.json"
            samplefile_path = f"yoga_toolkit/SampleVideo/TreePose/sample.mp4"
        elif type == 'WarriorII':
            roi = {
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
            angle_def = AngleNodeDef.WARRIOR_II_ANGLE
            jsonfile_path = f"yoga_toolkit/JsonFile/WarriorIIPose/sample.json"
            samplefile_path = f"yoga_toolkit/SampleVideo/WarriorIIPose/sample.mp4"
        elif type == 'ReversePlank':
            roi = {
                'NOSE': False,
                'LEFT_ELBOW': False,
                'LEFT_WRIST': False,
                'LEFT_INDEX': False,
                'LEFT_SHOULDER': False,
                'LEFT_HIP': False,
                'LEFT_KNEE': False
            }
            angle_def = AngleNodeDef.REVERSE_PLANK_ANGLE
            jsonfile_path = f"yoga_toolkit/JsonFile/ReversePlankPose/sample.json"
            samplefile_path = f"yoga_toolkit/SampleVideo/ReversePlankPose/sample.mp4"
        elif type == "Plank":
            roi = {
                'NOSE': False,
                'RIGHT_ANKLE': False,
                'RIGHT_KNEE': False,
                'LEFT_ANKLE': False,
                'LEFT_KNEE': False,
                'LEFT_HIP': False,
                'RIGHT_HIP': False,
                'LEFT_SHOULDER': False,
                'RIGHT_SHOULDER': False,
                'LEFT_ELBOW': False,
                'RIGHT_ELBOW': False
            }
            angle_def = AngleNodeDef.PLANK_ANGLE
            jsonfile_path = f"yoga_toolkit/JsonFile/PlankPose/sample.json"
            samplefile_path = f"yoga_toolkit/SampleVideo/PlankPose/sample.mp4"
        return roi, angle_def, jsonfile_path, samplefile_path
    
    def initialAngleDict(self, dict={}):
        index = 0
        for key,_ in self.angle_def.items():
            dict[key] = 0
            index+=1
        return dict
    
    def initialDetect(self):
        self.sample_angle_dict = toolkit.readSampleJsonFile(self.jsonfile_path)
        if self.sample_angle_dict == None:
            self.sample(self.samplefile_path, self.jsonfile_path)
            self.sample_angle_dict = toolkit.readSampleJsonFile(self.jsonfile_path)
        
    def sample(self, video_path, storage_path):
        '''
        Sample angle and storage to json
        return: None
        '''
        print(f"Sampling {video_path}...")
        sum_angle = np.zeros(len(self.angle_def))
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
            for _,value in self.angle_def.items():
                angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                     list(toolkit.getLandmarks(point3d[value[1]])), 
                                     list(toolkit.getLandmarks(point3d[value[2]])))
                perFrameOfAngle.append(angle)
            sum_angle+=perFrameOfAngle
        print(sum_angle/frame_count) # 平均角度
        sum_angle/=frame_count
        toolkit.writeSampleJsonFile(sum_angle, self.angle_def, storage_path)
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
        for key,value in self.angle_def.items():
            angle = toolkit.computeAngle(list(toolkit.getLandmarks(point3d[value[0]])), 
                                    list(toolkit.getLandmarks(point3d[value[1]])), 
                                    list(toolkit.getLandmarks(point3d[value[2]])))
            self.angle_dict[key] = angle
        # print(self.sample_angle_dict)
        # print(self.angle_dict)
        if(self.type == 'Tree'):
            self.roi, self.tips = toolkit.treePoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'WarriorII'):
            self.roi, self.tips = toolkit.WarriorIIPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'ReversePlank'):
            self.roi, self.tips = toolkit.ReversePlankPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Plank'):
            self.roi, self.tips = toolkit.PlankPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)

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