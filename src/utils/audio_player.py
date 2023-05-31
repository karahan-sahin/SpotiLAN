from pydub import AudioSegment, playback

class AudioPlayer:
    
    def __init__(self) -> None:
        self.ff = None
        pass
    
    def play(self, title):
        seg = AudioSegment.from_file(title)
        self.ff = playback._play_with_simpleaudio(seg)
        
    def stop(self):
        self.ff.stop()