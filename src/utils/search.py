import os   
from pytube import YouTube, Search

class Searcher():
    
    def __init__(self) -> None:
        self.PATH =  "."
        self.results = []
        self.downloaded_songs = []
            
    def fetchDownloaded(self):
        pass
    
    def searchSong(self, query, topN=5):
        from pytube import YouTube, Search
        s = Search(query)
        results = []
        for v in s.results:
            results.append({
                "title": v.title,
                "url": v.watch_url,
                "is_downloaded": True if v.title in self.downloaded_songs else False})
        
        return results

    def downloadSong(self, url, path):
    
        # url input from user
        yt = YouTube(url)
        
        # extract only audio
        video = yt.streams.filter(only_audio=True).first()
            
        # download the file
        out_file = video.download(output_path=path)
        
        # save the file
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        
        # result of success
        print(yt.title + " has been successfully downloaded.")