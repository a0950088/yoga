import tkinter as tk
import pyttsx3
from PIL import Image, ImageTk
import threading
from yoga_toolkit.correction_toolkit import *

class Calibration(tk.Frame):
	def __init__(self, master, name=None, vs=None):
		super().__init__(master)
		self.master = master
		self.is_running = False

		tk.Label(self, text='Calibration Stage', fg='#B15BFF', font=('Comic Sans MS', 30, 'bold')).place(x=450, y=15)
		icon = Image.open('data/image/finish.jpg').resize((50, 50))
		iconimage = ImageTk.PhotoImage(icon)
		self.finish_btn = tk.Button(self, text='Finish', image=iconimage, command=self.stop)
		self.finish_btn.photo = iconimage
		self.finish_btn.place(x=1150, y=700)
		self.hint = tk.Label(self, text='請調整瑜珈墊與鏡頭，使瑜珈墊放至框線當中', fg='#0072E3', font=('微軟正黑體', 16))
		self.hint.place(x=400, y=700)

		""" webcam """
		self.width, self.height = 750, 500
		self.canvas = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas.place(x=280, y=150)

		self.vs = vs
		self.thread = threading.Thread(target=self.update, daemon=True)

		self.engine = pyttsx3.init()
		self.engine.setProperty('rate', 150)
		self.voice_thread = threading.Thread(target=self.voice, daemon=True)

		self.start()
		
	def voice(self):
		result = self.hint.cget("text")
		self.engine.say(result)
		self.engine.runAndWait()

	def start(self):
		self.is_running = True
		self.thread.start()
		self.voice_thread.start()

	def update(self):
		while self.is_running:
			frame = self.vs.frame
			if frame is not None:
				try:
					frame = correction(frame)
					frame = cv2.flip(frame, 180)
					frame = cv2.resize(frame, (self.width, self.height))
					photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
					self.canvas.create_image(0, 0, anchor='nw', image=photo_image)
					self.canvas.image = photo_image
					self.canvas.update()
				except:
					print('cap stop')

	def stop(self):
		self.is_running = False
		
		from UI.Menu import Menu
		self.master.switch_frame(Menu, vs=self.vs)
