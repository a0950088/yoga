import threading
import pygame

class MusicPlayer:
	def __init__(self):
		pygame.mixer.init()
		pygame.mixer.music.load("./data/music/slow-boat-meditation-7744.mp3")
		pygame.mixer.music.set_volume(0.3)
		self.music_playing = False

		self.music_thread = threading.Thread(target=self.update, daemon=True)

	def start(self):
		self.music_playing = True
		pygame.mixer.music.play(-1)
		self.music_thread.start()		

	def update(self):
		while self.music_playing:
			pygame.time.Clock().tick(10)

	def stop(self):
		if pygame.mixer.music.get_busy():
			self.music_playing = False
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
