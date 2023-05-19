import pygame
import queue


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = queue.Queue()
        self.current_song = None

    def load(self, file_path):
        self.playlist.put(file_path)

    def play(self):
        if self.current_song is None or not pygame.mixer.music.get_busy():
            if not self.playlist.empty():
                song = self.playlist.get()
                self.current_song = song
                pygame.mixer.music.load(song)
                pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()
        self.current_song = None

    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def add_to_playlist(self, file_path):
        self.playlist.put(file_path)

    def clear_playlist(self):
        self.playlist = queue.Queue()


if __name__ == '__main__':
    # Usage example
    audio_player = AudioPlayer()

    # Add songs to the playlist
    audio_player.add_to_playlist("path/to/audio/song1.mp3")
    audio_player.add_to_playlist("path/to/audio/song2.mp3")
    audio_player.add_to_playlist("path/to/audio/song3.mp3")

    # Start playing the playlist
    audio_player.play()

    # Wait for song to finish
    while audio_player.is_playing():
        pass

    # Add more songs to the playlist
    audio_player.add_to_playlist("path/to/audio/song4.mp3")
    audio_player.add_to_playlist("path/to/audio/song5.mp3")

    # Start playing the updated playlist
    audio_player.play()

    # Wait for song to finish
    while audio_player.is_playing():
        pass

    # Clear the playlist
    audio_player.clear_playlist()
