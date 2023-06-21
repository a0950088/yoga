import yogaToolkit as yoga
import os

CWD = os.getcwd()
# sample angle
sampleVideoPath = f"{CWD}/TreePose/Video/sample/sample1.mp4"
sampleStoragePath = f"{CWD}/TreePose/SampleJson"
yoga.sampleVideo(sampleVideoPath, sampleStoragePath)

# read json
sampleJsonFilePath = f"{CWD}/TreePose/SampleJson/sample2.json"
sampleAngle = yoga.readSampleJsonFile(sampleJsonFilePath)

# detect video
detectVideoPath = f"{CWD}/TreePose/Video/detect/test4.mp4"
storageOutputVideoPath = f"{CWD}/TreePose/Video/output/test4.mp4"
yoga.detectVideo(detectVideoPath, storageOutputVideoPath, sampleAngle)

# detect image
detectImagePath = [f"{CWD}/test.jpg",f"{CWD}/test2.jpg",f"{CWD}/test3.jpg"]
storageOutputImagePath = f"{CWD}"
yoga.detectImage(detectImagePath, storageOutputImagePath, sampleAngle)