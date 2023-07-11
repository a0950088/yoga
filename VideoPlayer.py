import cv2
import threading
from PIL import Image, ImageTk
import time


class VideoPlayer:
	def __init__(self, video_path, canvas):
		self.canvas = canvas
		self.video = cv2.VideoCapture(video_path)
		self.fps = self.video.get(cv2.CAP_PROP_FPS)
		self.is_playing = False

		self.video_thread = threading.Thread(target=self.update)
		self.video_thread.daemon = True

	def start(self):
		self.is_playing = True
		self.video_thread.start()

	def update(self):
		while self.is_playing:
			init_t = time.time()
			ret, frame = self.video.read()
			if not ret:
				self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)				
			else:
				try:
					self.is_delay = False
					frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
					frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
					photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
					self.canvas.create_image(0, 0, anchor='nw', image=photo_image)
					self.canvas.image = photo_image
					self.canvas.update()
				except:
					print('stop video stream')

				self.delay = 1/self.fps - (time.time()-init_t)
				time.sleep(self.delay if self.delay > 0 else 0)
	
	def stop(self):
		self.is_playing = False
		self.video.release()
