import time
import multiprocessing
from pydub import AudioSegment, playback


def wait(duration): time.sleep(duration)


class AudioPlayer:

    def __init__(self):
        self.queue = []
        self.audio_file = ""
        self.current_idx = 0
        self.is_playing = None
        self.playback = None

    def play(self):
        if not self.is_playing:
            if not self.audio_file: self.audio_file = self.queue[0]

            self.audio_segment = AudioSegment.from_file(self.audio_file)
            # print("Playing...", self.audio_file, f"{self.queue=}")
            self.playback = playback._play_with_simpleaudio(self.audio_segment)
            self.is_playing = True

            self.process = multiprocessing.Process(target=wait, args=(self.audio_segment.duration_seconds,))
            self.process.start()

    def next_song(self):
        print("Terminating.....")
        self.process.terminate()
        self.playback.stop()
        self.is_playing = False
        if self.current_idx < len(self.queue) - 1:
            self.current_idx += 1
            self.audio_file = self.queue[self.current_idx]
            self.play()
            print("Playing from queue...")
        else:
            print("No more songs left ahead....")

    def previous_song(self):
        self.process.terminate()
        self.playback.stop()
        self.is_playing = False
        if self.current_idx > 0:
            self.current_idx -= 1
            self.audio_file = self.queue[self.current_idx]
            self.play()
        else:
            print("No more songs left behind....")

    def stop(self):
        self.playing.terminate()

    def set_volume(self, volume):
        self.audio_segment.set_volume(volume)

    def add_to_queue(self, audio_file):
        self.queue.append(audio_file)


if __name__ == "__main__":
    import os
    import sys

    # print(os.getcwd())
    # sys.exit(1)
    player = AudioPlayer()
    player.add_to_queue("musics/KuzuKuzu.mp3")
    player.add_to_queue("musics/Geççek.mp3")

    player.play()
    time.sleep(1)

    player.next_song()
    print(player.current_idx)
    time.sleep(1)

    player.previous_song()
    print(player.current_idx)
    time.sleep(1)

    player.previous_song()
    print(player.current_idx)
    time.sleep(1)

    player.next_song()
    print(player.current_idx)
    time.sleep(1)

    player.next_song()
    print(player.current_idx)
    time.sleep(1)
    print(player.current_idx)
    player.next_song()
