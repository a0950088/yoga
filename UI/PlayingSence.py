import tkinter as tk
import pyttsx3
from PIL import Image, ImageTk
import threading
import tools.VideoPath as VideoPath
from tools.VideoPlayer import VideoPlayer
from yoga_toolkit.yogaPose import *

class StartPlay(tk.Frame):
	def __init__(self, master, name, vs):
		super().__init__(master)
		self.master = master
		self.is_running = False
		
		tk.Label(self, text=name, font=('Comic Sans MS', 30, 'bold'), fg='#B15BFF').place(x=500, y=15)
		""" hint """
		self.hint_text = tk.StringVar()
		self.hint_text.set('開始偵測...')
		tk.Label(self, textvariable=self.hint_text, font=('微軟正黑體', 16), fg='#B15BFF').place(x=50, y=680)
		icon = Image.open('data/image/return.jpg').resize((50, 50))
		iconimage = ImageTk.PhotoImage(icon)
		return_btn = tk.Button(self, text='Return', image=iconimage, command=self.stop)
		return_btn.photo = iconimage
		return_btn.place(x=1150, y=10)

		self.width, self.height = 600, 500

		""" video """
		self.canvas_video = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas_video.place(x=20, y=100)
		video_path = VideoPath.Yoga_Video[name]
		self.player = VideoPlayer(video_path, self.canvas_video)

		""" webcam """
		self.canvas_cam = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas_cam.place(x=650, y=100)
		self.vs = vs
		self.thread = threading.Thread(target=self.cap_update, daemon=True)

		""" counting """
		self.count = tk.StringVar()
		tk.Label(self, textvariable=self.count, font=('微軟正黑體', 40, 'bold'), fg='#F00078', bg='#D0D0D0').place(x=680, y=150)
		self.counting_thread = threading.Thread(target=self.counting, daemon=True)

		""" detect model"""
		self.model = YogaPose(VideoPath.Yoga_Model[name])
		self.model.initialDetect()

		""" audio """
		self.engine = pyttsx3.init()
		self.engine.setProperty('rate', 150)
		self.voice_thread = threading.Thread(target=self.voice, daemon=True)

		""" heatmap """
		heatmap = Image.open('data/image/heatmap.png').resize((self.width, 150))
		heatmap = ImageTk.PhotoImage(heatmap)
		w, h = heatmap.width(), heatmap.height()
		self.canvas_heatmap = tk.Canvas(self, width=w, height=h)
		self.canvas_heatmap.place(x=650, y=620)
		self.canvas_heatmap.create_image(0, 0, anchor='nw', image=heatmap)
		self.canvas_heatmap.image = heatmap

		self.cap_start()
		self.player.start()

	def counting(self):
		try:
			tmp = int(self.count.get())
		except:
			print('not yet')
		while tmp > -1:
			self.count.set(tmp)
			time.sleep(1)
			if tmp == 0:
				tk.messagebox.showinfo("Time's up", "comment here...")
				self.count.set("")
			tmp -= 1

	def cap_start(self):
		self.is_running = True
		self.thread.start()
		self.voice_thread.start()

	def cap_update(self):
		while self.is_running:
			frame = self.vs.frame
			if frame is not None:
				try:
					frame = cv2.resize(frame, (self.width, self.height))
					frame = self.model.detect(frame, self.width, self.height, False)
					frame = cv2.flip(frame, 180)
					photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
					self.canvas_cam.create_image(0, 0, anchor='nw', image=photo_image)
					self.canvas_cam.image = photo_image
					self.canvas_cam.update()
					self.hint_text.set(self.model.tips)

					if self.model.tips == "動作正確":
						self.count.set(10)
						self.counting_thread.start()
				except:
					print('cap stop')

	def voice(self):
		while self.is_running:
			try:
				result = self.hint_text.get()
				self.engine.say(result)
				self.engine.runAndWait()
				time.sleep(2)
			except:
				# print('speech stop')
				pass

	def stop(self):
		self.is_running = False
		self.player.stop()
		from UI.Menu import Menu
		self.master.switch_frame(Menu, vs=self.vs)
