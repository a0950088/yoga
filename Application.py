import tkinter as tk
import tkinter.messagebox
import os
from CameraStream import *
from VideoPlayer import *
import VideoPath
from yoga_toolkit.correction_toolkit import *
from yoga_toolkit.yogaPose import *
import pyttsx3
import time

class startPage(tk.Frame):
	def __init__(self, master, name=None, vs=None):
		super().__init__(master)

		""" background """
		back_img = Image.open('data/image/background.jpg').resize((1250, 700))
		back_img = ImageTk.PhotoImage(back_img)
		w, h = back_img.width(), back_img.height()
		canvas = tk.Canvas(self, width=w, height=h)
		canvas.place(x=0, y=0)
		canvas.create_image(0, 0, anchor='nw', image=back_img)
		canvas.image = back_img

		label1 = tk.Label(self, text='Yoga Sample App', font=('Comic Sans MS', 36), fg='#B15BFF').place(x=380, y=100, relwidth=0.4, relheight=0.10)
		tk.Button(self, text='Start', bg='#DDDDFF', font=('Comic Sans MS', 16), 
			command=lambda: master.switch_frame(Correction, vs=vs)).place(x=500, y=400, relwidth=0.18, relheight=0.10)

class Correction(tk.Frame):
	def __init__(self, master, name=None, vs=None):
		super().__init__(master)
		self.master = master
		self.is_running = False

		tk.Label(self, text='Correction Stage', fg='#B15BFF', font=('Comic Sans MS', 24, 'bold')).place(x=450, y=15, relwidth=0.22, relheight=0.07)
		self.finish_btn = tk.Button(self, text='Finish', bg='#DDDDFF', font=('Comic Sans MS', 13), command=self.stop)
		self.finish_btn.place(x=1100, y=600, relwidth=0.08, relheight=0.06)
		self.hint = tk.Label(self, text='請調整瑜珈墊與鏡頭，使瑜珈墊放至框線當中', fg='#0072E3', font=('微軟正黑體', 16))
		self.hint.place(x=400, y=620)

		""" webcam """
		self.width, self.height = 750, 500
		self.canvas = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas.place(x=250, y=100)

		self.vs = vs
		self.thread = threading.Thread(target=self.update)
		self.thread.daemon = True

		self.engine = pyttsx3.init()
		self.engine.setProperty('rate', 150)
		self.voice_thread = threading.Thread(target=self.voice)
		self.voice_thread.daemon = True

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

		tk.Label(self, text='Menu', font=('Comic Sans MS', 24, 'bold'), fg='#B15BFF').place(x=500, y=15, relwidth=0.22, relheight=0.07)
		tk.Button(self, text='Tree Style', bg='#DDDDFF', font=('Comic Sans MS', 13), 
			command=lambda: master.switch_frame(StartPlay, 'Tree Style', self.vs)).place(x=320, y=100, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Warrior2 Style', bg='#DDDDFF', font=('Comic Sans MS', 13), 
			command=lambda: master.switch_frame(StartPlay, 'Warrior2 Style', self.vs)).place(x=720, y=100, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Plank', bg='#DDDDFF', font=('Comic Sans MS', 13), 
			command=lambda: master.switch_frame(StartPlay, 'Plank', self.vs)).place(x=320, y=200, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Reverse Plank', bg='#DDDDFF', font=('Comic Sans MS', 13), 
			command=lambda: master.switch_frame(StartPlay, 'Reverse Plank', self.vs)).place(x=720, y=200, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Warrior1 Style', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=320, y=300, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Warrior3 Style', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=720, y=300, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='cow face pose', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=320, y=400, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Downward-Facing Dog', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=720, y=400, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Bow pose', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=320, y=500, relwidth=0.17, relheight=0.08)
		tk.Button(self, text='Bridge pose', bg='#DDDDFF', font=('Comic Sans MS', 13)).place(x=720, y=500, relwidth=0.17, relheight=0.08)

		tk.Button(self, text='Return', bg='#DDDDFF', font=('Comic Sans MS', 13), command=lambda: master.switch_frame(startPage, vs=self.vs)).place(x=1100, y=15)

class StartPlay(tk.Frame):
	def __init__(self, master, name, vs):
		super().__init__(master)
		self.master = master
		self.is_running = False
		
		tk.Label(self, text=name, font=('Comic Sans MS', 24, 'bold'), fg='#B15BFF').place(x=400, y=15, relwidth=0.22, relheight=0.07)
		self.hint_text = tk.StringVar()
		self.hint_text.set('開始偵測...')
		tk.Label(self, textvariable=self.hint_text, font=('微軟正黑體', 16), fg='#B15BFF').place(x=700, y=620)
		tk.Button(self, text='Return', bg='#DDDDFF', font=('Comic Sans MS', 13), command=self.stop).place(x=1100, y=10)
		# tk.Button(self, text='Play', bg='#DDDDFF', font=('Comic Sans MS', 13), command=self.video_resume).place(x=200, y=620, relwidth=0.06, relheight=0.06)
		# tk.Button(self, text='Stop', bg='#DDDDFF', font=('Comic Sans MS', 13), command=self.video_stop).place(x=300, y=620, relwidth=0.06, relheight=0.06)
		
		self.width, self.height = 600, 500
		""" video """
		self.canvas1 = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas1.place(x=20, y=100)

		video_path = VideoPath.Yoga_Video[name]
		self.player = VideoPlayer(video_path, self.canvas1)

		""" webcam """
		self.canvas2 = tk.Canvas(self, width=self.width, height=self.height)
		self.canvas2.place(x=630, y=100)

		self.vs = vs
		self.thread = threading.Thread(target=self.cap_update)
		self.thread.daemon = True

		""" detect model"""
		self.model = YogaPose(VideoPath.Yoga_Model[name])
		self.model.initialDetect()

		""" audio """
		self.engine = pyttsx3.init()
		self.engine.setProperty('rate', 150)
		self.voice_thread = threading.Thread(target=self.voice)
		self.voice_thread.daemon = True

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
					self.canvas2.create_image(0, 0, anchor='nw', image=photo_image)
					self.canvas2.image = photo_image
					self.canvas2.update()
					self.hint_text.set(self.model.tips)
				except:
					print('cap stop')

	def voice(self):
		while self.is_running:
			result = self.hint_text.get()
			self.engine.say(result)
			self.engine.runAndWait()
			time.sleep(2)

	# def video_stop(self):
	# 	self.player.pause()

	# def video_resume(self):
	# 	self.player.play()

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
		back_img = Image.open('data/image/background.jpg').resize((1250, 700))
		back_img = ImageTk.PhotoImage(back_img)
		w, h = back_img.width(), back_img.height()
		self.resizable(height=False, width=False)
		self.geometry('%dx%d+300+100' % (w, h))
		self.attributes('-alpha', 1)

		""" camera """
		self.vs = CameraStream()
		self.vs.start()

		""" init frame """
		self.now_frame = None
		self.switch_frame(startPage, vs=self.vs)

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
		self.quit()
		self.destroy()
		try:
			os._exit(0)
		except:
			print('os.exit')


if __name__ == "__main__":
	app = App()
	app.mainloop()
