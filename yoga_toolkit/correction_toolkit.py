import cv2
import matplotlib.pyplot as plt
import numpy as np

def correction(image):
	image_width, image_height = image.shape[1], image.shape[0]

	''' calculate the correction bounding box'''
	center_x , center_y = int(image_width / 2), int(image_height * 0.85)
	rectangle = np.array([[center_x - 0.3 * image_width, center_y - 0.07 * image_height], [center_x - 0.38 * image_width, center_y + 0.07 * image_height], [center_x + 0.38 * image_width, center_y + 0.07 * image_height], [center_x + 0.3 * image_width, center_y - 0.07 * image_height]], np.int32)
	cv2.polylines(image, [rectangle], True, (255, 0, 0), 2) 
	return image


if __name__ == '__main__':
	image = cv2.imread('./Dataset/Plank/3.jpg')
	cv2.imshow('l', correction(image))
	cv2.waitKey(0)
	cv2.destroyAllWindows()


