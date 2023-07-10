import cv2
import threading
from PIL import Image, ImageTk

class VideoPlayer:
	def __init__(self, video_path, canvas):
		self.canvas = canvas
		self.video = cv2.VideoCapture(video_path)
		self.is_playing = False
		# self.pause_event = threading.Event()

		# """ init image """
		# frame = Image.open('data/image/sample.png').resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
		# photo_image = ImageTk.PhotoImage(frame)
		# self.canvas.create_image(0, 0, anchor='nw', image=photo_image)
		# self.canvas.image = photo_image

		self.thread = threading.Thread(target=self.update)
		self.thread.daemon = True

	def start(self):
		self.is_playing = True
		self.thread.start()
		# self.pause_event.clear()

	def update(self):
		while True:
			while self.is_playing:
				# if not self.pause_event.is_set():
				ret, frame = self.video.read()
				if not ret:
					break
				try:
					frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
					frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
					photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
					self.canvas.create_image(0, 0, anchor='nw', image=photo_image)
					self.canvas.image = photo_image
					self.canvas.update()
				except:
					print('stop video stream')
				# else:
				# 	self.pause_event.wait()
				# 	print('wait')
	
	def stop(self):
		self.is_playing = False
		self.video.release()

	# def pause(self):
	# 	if self.is_playing:
	# 		self.pause_event.set()

	# def play(self):
	# 	if not self.is_playing:
	# 		self.start()
	# 	elif self.pause_event.is_set():
	# 		print('pause')
	# 		self.pause_event.clear()
	# 	elif self.is_playing and not self.pause_event.is_set():
	# 		print('replay')
	# 		self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
	# 		self.start()
