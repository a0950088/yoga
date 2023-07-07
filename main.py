import os
import cv2
from yogaPose import WarriorIIPosture
CWD = os.getcwd().replace("\\","/")

IMAGE_FILES = ['./WarriorTwoPose/Image/detect/test1.jpg',
               './WarriorTwoPose/Image/detect/f1.jpg']
# sample video path
sample_path = f"{CWD}/WarriorTwoPose/Video/sample/Warrior2_Pose3_Trim.mp4"
file_name = (sample_path.split('/')[-1]).split('.')[0]
storage_path = f"{CWD}/WarriorTwoPose/SampleJson/sample_{file_name}.json"

# detect video path
video_path = f"{CWD}/WarriorTwoPose/Video/detect/test3.mp4"

warriorII = WarriorIIPosture()
warriorII.sample(sample_path, storage_path)

# if not warriorII.initialDetect():
#     print("Please check sample file exist, or run sample function.")
#     exit()

# detect image
# for idx, file in enumerate(IMAGE_FILES):
#     image = cv2.imread(file)
#     image_height, image_width, _ = image.shape
#     frame = warriorII.detect(image, image_width, image_height, True)
#     cv2.imshow('image',frame)
#     cv2.waitKey(0)
    
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
#     frame = warriorII.detect(frame, original_width, original_height, False)
#     print(warriorII.tips)
#     cv2.imshow('image',frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()