import yogaToolkit as yoga
import os

CWD = os.getcwd()
'''
1. TreePose
2. WarriorTwoPose
...
'''
YOGA_TYPE = "TreePose" 

SAMPLE_VIDEO_NAME = "sample1.mp4"
STORAGE_JSON_NAME = "sample1.json"
SAMPLE_VIDEO_PATH = f"{CWD}/{YOGA_TYPE}/Video/sample"
STORAGE_JSON_PATH = f"{CWD}/{YOGA_TYPE}/SampleJson"

DETECT_VIDEO_PATH = f"{CWD}/{YOGA_TYPE}/Video/detect"
STORAGE_VIDEO_PATH = f"{CWD}/{YOGA_TYPE}/Video/output"
DETECT_IMAGE_PATH = f"{CWD}/{YOGA_TYPE}/Image/detect"
STORAGE_IMAGE_PATH = f"{CWD}/{YOGA_TYPE}/Image/output"

# sample angle
# sampleVideoPath = f"{SAMPLE_VIDEO_PATH}/{SAMPLE_VIDEO_NAME}"
# sampleStoragePath = f"{STORAGE_JSON_PATH}/{STORAGE_JSON_NAME}"
# yoga.sampleVideo(sampleVideoPath, sampleStoragePath)

# read json
# jsonFile = "sample1.json"
# sampleJsonFilePath = f"{STORAGE_JSON_PATH}/{jsonFile}"
# sampleAngle = yoga.readSampleJsonFile(sampleJsonFilePath)

# detect video
# videoFile = "test4.mp4"
# detectVideoPath = f"{DETECT_VIDEO_PATH}/{videoFile}"
# storageOutputVideoPath = f"{STORAGE_VIDEO_PATH}/{videoFile}"
# yoga.detectVideo(detectVideoPath, storageOutputVideoPath, sampleAngle)

# detect image
# imageFiles = [f"{DETECT_IMAGE_PATH}/test.jpg", f"{DETECT_IMAGE_PATH}/test4.jpg"]
# storageOutputImagePath = f"{STORAGE_IMAGE_PATH}"
# yoga.detectImage(imageFiles, STORAGE_IMAGE_PATH, sampleAngle)

yoga.detectWebCam(f"{CWD}/testWebCam/test.mp4")