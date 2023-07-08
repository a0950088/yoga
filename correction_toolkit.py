import cv2
import matplotlib.pyplot as plt
import numpy as np

def correction(image):
	image_width, image_height = image.shape[1], image.shape[0]

	''' calculate the correction bounding box'''
	center_x , center_y = int(image_width / 2), int(image_height * 0.85)
	rectangle = np.array([[center_x - 380, center_y - 75], [center_x -498, center_y + 75], [center_x + 498, center_y + 75], [center_x + 380, center_y - 75]], np.int32)

	''' detect yoga mat(temporarily useless) '''
	# image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	# crop_img = image[rectangle[0][1]:rectangle[1][1], rectangle[1][0]:rectangle[2][0]]
	# low_green = np.array([50,20,40])
	# high_green = np.array([85,40,80])
	# mask = cv2.inRange(crop_img, low_green, high_green)

	cv2.polylines(image, [rectangle], True, (0, 0, 255), 2) 
	# plt.imshow(image)
	# plt.show()

	return image


if __name__ == '__main__':
	image = cv2.imread('./Dataset/pose (1).jpg')
	cv2.imshow('l', correction(image))
	cv2.waitKey(0)
	cv2.destroyAllWindows()


