import tkinter as tk
from tkinter import filedialog as fd
from PIL import ImageTk, Image
from correction import *
import cv2
import os

second_step = False

def select_file():
	global second_step
	filetypes = (("Video Files", "*.jpg;*.jpeg;*.png"), ('All files', '*.*'))
	File = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
	file = ""
	for i in range(len(File) - 1, 0, -1):
		if File[i] == '/':
			file = File[i+1:]
			break
	filename.set(file)

	if File:
		# show_frame(File)
		image = cv2.imread(File)
		image = cv2.resize(image, (width, height))
		result_image, landmarks = detect(image)
		result_image, correction_text = is_middle(result_image, landmarks)
		if correction_text == 'Centerline Correct':
			msgbox_text.insert('end', '請根據鏡頭調整距離鏡頭的遠近\n')
			result_image, result_text = is_distance_ok(result_image, landmarks)
			if result_text == 'Distance Correct':
				msgbox_text.insert('end', '校正結束\n')
				second_step = True
			else:
				msgbox_text.insert('end', result_text+'\n')
		else:
			msgbox_text.insert('end', correction_text+'\n')

		show_frame(result_image)


def show_frame(image):
	image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image_pil = Image.fromarray(image_rgb)
	image_tk = ImageTk.PhotoImage(image_pil)
	canvas1.itemconfig(image_on_canvas, image=image_tk)
	canvas1.image = image_tk
		
def _quit():
	root.quit()
	root.destroy()
	os._exit(0)


""" main """
root = tk.Tk()
root.title("yoga correction sample")

tk.Label(text="File name: ", font=('Comic Sans MS', 12)).grid(row=0, column=0)
filename = tk.StringVar()
print_filename = tk.Label(root, textvariable=filename, font=('Comic Sans MS', 12))
print_filename.grid(row=0, column=1)

photo = Image.open('./dic.png').resize((30, 30))
photoimage = ImageTk.PhotoImage(photo)
tk.Button(master=root, text='Select File', image=photoimage, font=('Comic Sans MS', 12), command=select_file).grid(row=0, column=2)
# tk.Button(master=root, text='Start', font=('Comic Sans MS', 12), command=Start).grid(row=0, column=3)
tk.Button(master=root, text='Exit', font=('Comic Sans MS', 12), command=_quit).grid(row=0, column=3)


""" img """
width, height = 800, 650
img = cv2.imread('./Dataset/correction/5.jpg')
img = cv2.resize(img, (width, height))
image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
image_pil = Image.fromarray(image_rgb)
tk_img = ImageTk.PhotoImage(image_pil)
canvas1 = tk.Canvas(root, width=width, height=height)
image_on_canvas = canvas1.create_image(0, 0, anchor='nw', image=tk_img)
canvas1.grid(row=1, column=0, columnspan=2)

""" text """
msgbox_text = tk.Text(root, height=20, width=50, font=('Comic Sans MS', 12))
msgbox_text.grid(row=1, column=3)
msgbox_text.delete('1.0', tk.END)
msgbox_text.insert('end', "請調整鏡頭角度\n請站在畫面正中間，雙手平舉，兩腳保持一步的距離\n")

initial()

root.mainloop()
