import simpleaudio as sa

class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename
        self.wave_obj = sa.WaveObject.from_mp3_file(filename)
        self.play_obj = None

    def play(self):
        self.play_obj = self.wave_obj.play()

    def stop(self):
        if self.play_obj:
            self.play_obj.stop()

    def is_playing(self):
        if self.play_obj:
            return self.play_obj.is_playing()
        else:
            return False

    def wait_done(self):
        if self.play_obj:
            self.play_obj.wait_done()


if __name__ == "__main__":
    player = AudioPlayer("audio.mp3")
    player.play()

    # Do something else while the audio is playing

    player.stop()