# import the necessary packages
from threading import Thread
import time
import cv2

class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
		self.start_time = time.time()
		self.font = cv2.FONT_HERSHEY_SIMPLEX

	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				break

			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
			assert self.grabbed, "Lost connection with camera!"
			cv2.putText(self.frame, "%0.3f" % (time.time()-self.start_time), (50,200), self.font, 2, (255,255,255),4,cv2.LINE_AA)
		self.stream.release()

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True