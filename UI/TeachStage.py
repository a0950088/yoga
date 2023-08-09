import tkinter as tk
from PIL import Image, ImageTk
import threading
import tools.VideoPath as VideoPath
from tools.VideoPlayer import VideoPlayer

class TeachStage(tk.Frame):
	def __init__(self, master, name, vs):
		super().__init__(master)
		self.master = master
		self.name = name
		self.vs = vs
		self.is_running = False

		tk.Label(self, text=name, font=('Comic Sans MS', 30, 'bold'), fg='#B15BFF').place(x=500, y=15)
		tk.Label(self, text='影片教學', font=('微軟正黑體', 20), fg='#FFAAD5').place(x=540, y=85)
		icon = Image.open('data/image/finish.jpg').resize((50, 50))
		iconimage = ImageTk.PhotoImage(icon)
		self.finish_btn = tk.Button(self, text='Finish', image=iconimage, command=self.stop)
		self.finish_btn.photo = iconimage
		self.finish_btn.place(x=1150, y=700)

		self.width, self.height = 950, 500

		""" video """
		self.canvas_video = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas_video.place(x=150, y=150)
		video_path = VideoPath.Yoga_Video[name]
		self.player = VideoPlayer(video_path, self.canvas_video)

		self.start()

	def start(self):
		self.is_running = True
		self.player.start()
	
	def stop(self):
		self.is_running = False
		self.player.stop()

		from UI.PlayingSence import StartPlay
		self.master.switch_frame(StartPlay, name=self.name, vs=self.vs)