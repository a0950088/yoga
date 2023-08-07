import cv2
import threading
import datetime

class CameraStream:
	def __init__(self):
		self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		self.is_running = False
		self.frame = None
		
		""" save original frame"""
		current_date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		filename = f"./output_{current_date_time}.avi"
		self.output = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'XVID'), 30.0, (640, 480))
		
		self.thread = threading.Thread(target=self.update, daemon=True)

	def start(self):
		self.is_running = True
		self.thread.start()

	def update(self):
		while self.is_running:
			ret, frame = self.cap.read()
			self.output.write(frame)
			if not ret:
				break
			try:
				self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			except:
				print('stop cap stream')

	def stop(self):	
		self.is_running = False
		self.cap.release()
		self.output.release()
		