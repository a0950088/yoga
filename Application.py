import tkinter as tk
import tkinter.messagebox
import os
from CameraStream import *
from VideoPlayer import *
from MusicPlayer import *
import VideoPath
from yoga_toolkit.correction_toolkit import *
from yoga_toolkit.yogaPose import *
import pyttsx3

class StartPage(tk.Frame):
	def __init__(self, master, name=None, vs=None):
		super().__init__(master)

		""" background """
		back_img = Image.open('data/image/background.jpg').resize((1280, 800))
		back_img = ImageTk.PhotoImage(back_img)
		w, h = back_img.width(), back_img.height()
		canvas = tk.Canvas(self, width=w, height=h)
		canvas.place(x=0, y=0)
		canvas.create_image(0, 0, anchor='nw', image=back_img)
		canvas.image = back_img

		label1 = tk.Label(self, text='Yoga Sample App', font=('Comic Sans MS', 36), fg='#B15BFF').place(x=380, y=100, relwidth=0.4, relheight=0.10)
		tk.Button(self, text='Start', bg='#DDDDFF', font=('Comic Sans MS', 18), 
			command=lambda: master.switch_frame(Calibration, vs=vs), 
			activeforeground='#ADADAD').place(x=520, y=450, relwidth=0.18, relheight=0.10)

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
		self.master.switch_frame(Menu, vs=self.vs)

class Menu(tk.Frame):
	def __init__(self, master, name=None, vs=None):
		super().__init__(master)
		self.master = master
		self.vs = vs

		tk.Label(self, text='Menu', font=('Comic Sans MS', 30, 'bold'), fg='#B15BFF').place(x=500, y=15, relwidth=0.22, relheight=0.07)
		tk.Button(self, text='Tree Style', bg='#DDDDFF', font=('Comic Sans MS', 14), activeforeground='#ADADAD',
			command=lambda: master.switch_frame(StartPlay, 'Tree Style', self.vs)).place(x=320, y=150, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Warrior2 Style', bg='#DDDDFF', font=('Comic Sans MS', 14), activeforeground='#ADADAD',
			command=lambda: master.switch_frame(StartPlay, 'Warrior2 Style', self.vs)).place(x=720, y=150, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Plank', bg='#DDDDFF', font=('Comic Sans MS', 14), activeforeground='#ADADAD',
			command=lambda: master.switch_frame(StartPlay, 'Plank', self.vs)).place(x=320, y=250, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Reverse Plank', bg='#DDDDFF', font=('Comic Sans MS', 14), activeforeground='#ADADAD',
			command=lambda: master.switch_frame(StartPlay, 'Reverse Plank', self.vs)).place(x=720, y=250, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Child\'s pose', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=320, y=350, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Seated Forward Bend', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=720, y=350, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Low Lunge', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=320, y=450, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Downward dog', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=720, y=450, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Pyramid pose', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=320, y=550, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Bridge pose', bg='#DDDDFF', font=('Comic Sans MS', 14)).place(x=720, y=550, relwidth=0.17, relheight=0.08)

		icon = Image.open('data/image/return.jpg').resize((50, 50))
		iconimage = ImageTk.PhotoImage(icon)
		return_btn = tk.Button(self, text='Return', image=iconimage, command=lambda: master.switch_frame(StartPage, vs=self.vs))
		return_btn.photo = iconimage
		return_btn.place(x=1150, y=15)

class StartPlay(tk.Frame):
	def __init__(self, master, name, vs):
		super().__init__(master)
		self.master = master
		self.is_running = False
		
		tk.Label(self, text=name, font=('Comic Sans MS', 30, 'bold'), fg='#B15BFF').place(x=500, y=15)
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
		self.master.switch_frame(Menu, vs=self.vs)

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Yoga sample")

		""" menu """
		menu_bar = tk.Menu(self)

		filemenu = tk.Menu(menu_bar, tearoff=0)
		menu_bar.add_cascade(label='File', menu=filemenu)
		filemenu.add_command(label='Exit', command=self._quit)

		menu_bar.add_cascade(label='Edit')
		menu_bar.add_cascade(label='About', command=self.show_info)
		menu_bar.add_cascade(label='Help')
		self['menu'] = menu_bar

		""" window size """
		back_img = Image.open('data/image/background.jpg').resize((1280, 800))
		back_img = ImageTk.PhotoImage(back_img)
		w, h = back_img.width(), back_img.height()
		self.resizable(height=False, width=False)
		self.geometry('%dx%d+300+100' % (w, h))
		self.attributes('-alpha', 1)

		""" camera """
		self.vs = CameraStream()
		self.vs.start()

		""" background music """
		self.bg_music = MusicPlayer()
		self.bg_music.start()

		""" init frame """
		self.now_frame = None
		self.switch_frame(StartPage, vs=self.vs)

		self.protocol("WM_DELETE_WINDOW", self._quit)

	def switch_frame(self, frame_class, name=None, vs=None):
		new_frame = frame_class(self, name, vs)
		if self.now_frame is not None:
			self.now_frame.destroy()
		self.now_frame = new_frame
		self.now_frame.pack(side='top', fill='both', expand=1)

	def show_info(self):
		tk.messagebox.showinfo("About", "This is a correction sample system.")

	def _quit(self):
		self.vs.stop()
		self.bg_music.stop()
		self.quit()
		self.destroy()
		try:
			os._exit(0)
		except:
			print('os.exit')

if __name__ == "__main__":
	app = App()
	app.mainloop()
