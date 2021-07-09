import tkinter as tk
from tkinter.filedialog import *
from tkinter import ttk

import carPlateIdentity
import cv2
from PIL import Image, ImageTk

import threading
import time
from datetime import datetime
from dao.Car import Car
from dao.CarManage import CarManage
import tkinter.messagebox



class Surface(ttk.Frame):
	pic_path = ""
	viewhigh = 600
	viewwide = 600
	update_time = 0
	thread = None
	thread_run = False
	camera = None
		
	def __init__(self, win):
		global tree
		ttk.Frame.__init__(self, win)
		frame_left = ttk.Frame(self)
		frame_right1 = ttk.Treeview(self)
		frame_right2 = ttk.Frame(self)
		win["height"] = 600
		win["width"] = 600
		win.title("车牌识别")
		self.pack(fill=tk.BOTH, expand=tk.YES, padx="5", pady="5")
		frame_left.pack(side=LEFT,expand=1,fill=BOTH)
		frame_right1.pack(side=TOP,expand=1,fill=tk.Y)
		frame_right2.pack(side=RIGHT,expand=0)
		ttk.Label(frame_left, text='车辆图像：').pack(anchor="nw")
		ttk.Label(frame_right1, text='车辆识别结果')

		ac = ('a', 'b', 'c', 'd')
		self.tree = ttk.Treeview(frame_right1, columns = ac, show='headings',height = 10)
		self.vbar = ttk.Scrollbar(frame_right1, orient=VERTICAL, command=self.tree.yview)
		self.tree.column("a", width=100, anchor="center")
		self.tree.column("b", width=200, anchor="center")
		self.tree.column("c", width=200, anchor="center")
		self.tree.column("d", width=50, anchor="center")
		self.tree.heading("a", text="车牌号码")
		self.tree.heading("b", text="入库时间")
		self.tree.heading("c", text="出库时间")
		self.tree.heading("d", text="费用")

		from_pic_ctl = ttk.Button(frame_right2, text="来自图片", width=20, command=self.from_pic)
		from_vedio_ctl = ttk.Button(frame_right2, text="来自摄像头", width=20, command=self.from_vedio)
		self.image_ctl = ttk.Label(frame_left)
		self.image_ctl.pack(anchor="nw")


		from_vedio_ctl.pack(anchor="se", pady="5")
		from_pic_ctl.pack(anchor="se", pady="5")


	def get_imgtk(self, img_bgr):
		img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
		im = Image.fromarray(img)
		imgtk = ImageTk.PhotoImage(image=im)
		wide = imgtk.width()
		high = imgtk.height()
		if wide > self.viewwide or high > self.viewhigh:
			wide_factor = self.viewwide / wide
			high_factor = self.viewhigh / high
			factor = min(wide_factor, high_factor)

			wide = int(wide * factor)
			if wide <= 0 : wide = 1
			high = int(high * factor)
			if high <= 0 : high = 1
			im=im.resize((wide, high), Image.ANTIALIAS)
			imgtk = ImageTk.PhotoImage(image=im)
		return imgtk
	
	def show_result(self, predict_result):
		if predict_result:
			car = Car()
			carmanage = CarManage()
			car.CarPN = predict_result
			results = carmanage.Leave(car)
			if len(results) != 0:
				car.TimeIn = results[0][2]
				car.TimeOut = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				time_1_in = datetime.strptime(car.TimeIn, "%Y-%m-%d %H:%M:%S")
				time_2_out = datetime.strptime(car.TimeOut, "%Y-%m-%d %H:%M:%S")
				total_seconds = (time_2_out - time_1_in).total_seconds()
				car.PayVal = (total_seconds / 3600) * 50
				carmanage.Update(car)

				self.tree.insert("", "end", values=(car.CarPN,car.TimeIn,car.TimeOut,str(car.PayVal)))
				self.tree.grid(row=0, column=0, sticky=NSEW)
				self.vbar.grid(row=0, column=1, sticky=NS)
				tk.messagebox.showinfo(title='车辆识别',message=car.CarPN+' \n入库时间：'+car.TimeIn+ '\n 出库时间：'  +car.TimeOut+'\n共计：' +str(round(car.PayVal,2)))
			else:
				car.TimeIn = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
				carmanage.Enter(car)
				tk.messagebox.showinfo(title='车辆识别',message='欢迎光临！'+ car.CarPN +' \n入库时间：'+car.TimeIn)
		else:
			tk.messagebox.showinfo(title='车辆识别', message='识别失败！\n请重新识别！')





	def from_vedio(self):
		if self.camera is None:
			self.camera = cv2.VideoCapture(0)
			if not self.camera.isOpened():
				self.camera = None
				return
		self.thread = threading.Thread(target=self.vedio_thread, args=(self,))
		self.thread.setDaemon(True)
		self.thread.start()
		self.thread_run = True
		
	def from_pic(self):

		self.pic_path = askopenfilename(title="选择识别图片", filetypes=[("jpg图片", "*.jpg")])
		if self.pic_path:
			img_bgr = cv2.imread(self.pic_path)

			self.imgtk = self.get_imgtk(img_bgr)
			self.image_ctl.configure(image=self.imgtk)

			# 释放资源
			self.camera.release()

			image = get_file_content("crap_FINSH.jpg")

			license = carPlateIdentity.predict(image)

			# 放入数据库
			self.show_result(license)


	@staticmethod
	def vedio_thread(self):

		self.camera.open(0)
		_, img_bgr = self.camera.read()
		cv2.imwrite('crap_FINSH.jpg', img_bgr)
		self.imgtk = self.get_imgtk(img_bgr)
		self.image_ctl.configure(image=self.imgtk)

		#释放资源
		self.camera.release()



		image = get_file_content("crap_FINSH.jpg")

		license = carPlateIdentity.predict(image)

		#放入数据库
		self.show_result(license)


def get_file_content(filePath):
	with open(filePath, 'rb') as fp:
			return fp.read()

def close_window():
	print("destroy")
	if surface.thread_run :
		surface.thread_run = False
		surface.thread.join(2.0)
	win.destroy()
	
	
if __name__ == '__main__':
	win=tk.Tk()
	
	surface = Surface(win)
	win.protocol('WM_DELETE_WINDOW', close_window)
	win.mainloop()
	
