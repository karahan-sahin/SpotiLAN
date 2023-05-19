from src.utils.search import Searcher
from src.utils.audio_player import AudioPlayer

#s = Searcher()
#
#song = s.searchSong("sting")[0]
#
#s.downloadSong(song.get("url"),  "./musics/")
#
import vlc
p = vlc.MediaPlayer("./musics/shape_of_my_heart.mp3")
p.play()