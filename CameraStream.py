import cv2
import threading

class CameraStream:
	def __init__(self):
		self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
		self.is_running = False
		self.frame = None
		self.output = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
		
		self.thread = threading.Thread(target=self.update)
		self.thread.daemon = True

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
		