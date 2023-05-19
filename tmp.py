import os

print(os.getcwd())
print(os.listdir("./musics"))

from pydub import AudioSegment
from pydub.playback import play

song = AudioSegment.from_mp3('./musics/KuzuKuzu.mp3')
play(song)