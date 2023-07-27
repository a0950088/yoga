import tkinter as tk
from PIL import Image, ImageTk
from UI.StartPage import StartPage
from UI.PlayingSence import StartPlay

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
