import tkinter as tk
from PIL import Image, ImageTk
from UI.Calibration import Calibration

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
