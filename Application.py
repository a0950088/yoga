import tkinter as tk
import tkinter.messagebox
import os
from PIL import Image, ImageTk
from tools.CameraStream import *
from tools.MusicPlayer import *
from UI.PlayingSence import StartPlay
from UI.StartPage import StartPage
from UI.Menu import Menu
from UI.Calibration import Calibration

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
