import os
import cv2
from yoga_toolkit.yogaPose import YogaPose
CWD = os.getcwd().replace("\\","/")

IMAGE_FILES = [f"{CWD}/yoga_toolkit/TreePose/Image/detect/test.jpg",
               f"{CWD}/yoga_toolkit/TreePose/Image/detect/test4.jpg",
               f"{CWD}/yoga_toolkit/TreePose/Image/detect/test5.jpg"]

'''
type: WarriorII, Tree, Plank, ReversePlank
'''
pose = YogaPose("ReversePlank")
pose.initialDetect()

# detect image
# for idx, file in enumerate(IMAGE_FILES):
#     image = cv2.imread(file)
#     image_height, image_width, _ = image.shape
#     frame = pose.detect(image, image_width, image_height, True)
#     cv2.imshow('image',frame)
#     cv2.waitKey(0)

# # detect video path
video_path = f"{CWD}/yoga_toolkit/ReversePlankPose/Video/detect/test3.mp4"
file_name = (video_path.split('/')[-1]).split('.')[0]
storage_path = f"{CWD}/yoga_toolkit/ReversePlankPose/Video/output/{file_name}.mp4"

cap = cv2.VideoCapture(video_path)
original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
output = cv2.VideoWriter(storage_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (original_width, original_height))
print(original_width,original_height)
fps = cap.get(cv2.CAP_PROP_FPS)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Video end")
        break
    frame = pose.detect(frame, original_width, original_height, False)
    print(pose.tips)
    cv2.imshow('image',frame)
    output.write(frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    
cap.release()
output.release()
cv2.destroyAllWindows()