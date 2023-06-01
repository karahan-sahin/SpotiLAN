# SpotiLAN

## How to run
From the project root execute the following command,

```
pip install -r requirements.txt
python3 -m main.src --name "user_name"
```

### Third-Party Library List

Libraries which will be used are:
1. flask
1. pytube
1. simpleaudio

## Components of User Interface

All components are shown via corresponding component within user-interface mockup diagram as below.

1. **General User Interface Component(s)**

    The user interface will be implement using streamlit library which provides dynamic front-end library for Python. Excluding audio-play component, all components of the user interface can be implemented using base streamlit library. 

2. **Audio Player Component**

    For audio-player component, the streamlit-player provides audio file manipulation within its API. 

    Audio player components include:
    1. Start Song Button
    2. Stop Song Button
    3. Go to Previous Song Button
    4. Go to Next Song Button

    which should be connected to the packet triggers to be broadcasted for users within the network session(?).

3. **Song Search Component**

    The SpotiLAN interface should provide a search bar component which is connected to the YouTube API via Python library pytube.

    The search component should have the functionality of adding songs to the playlist.

4. **Playlist Component**

    Playlist component should be implemented in order to control the music flow within the session.

    The component should be interacted for:
    1. Adding a Song
    1. Removing a Song

5. **Friend List Component**

    Friend List component should be implemented in order to see the online users within the session. The component should send discovery packets in 10 seconds intervals.




## User-Song Sync Implementation

This functionality is only required in Start Song action. 
Params: x, max(SEQ) 

Exhaustive synchronization:

| Client_1 (snd) | Delay Time Calculation - Client_2 (recvr) |
|----------------|-------------------------------------------|
| { timestamp: “m” }  | time.time_ns() - m = t0 | 
| { timestamp: “m+1” } | time.time_ns() - m+1 = t1 | 
| { timestamp: “m+2” } | time.time_ns() - m+2 = t2 | 
| START_TIME : x | START_TIME : START_TIME - mean([ t0, t1, t2, .., t10 ]) | 


## Network Packages

Assume that application run only with 2 user, the packages for this case would be as follows

1. \<START\> : This is TCP package to start the music simultaneously. Start time field corresponds to the reserved start time of the sender and receiver. The delay is required due to the clock sync issues between clients.
```python
{
    "type": "start",
    "name": "<id-of-the-song>",
    "start-time":"<timestamp + delay>"
}
```
2. \<STOP\> : This is a TCP package. User who sends a < STOP> package should wait until 3-way handshake then stop the music. User who receives the <STOP> package should stop the music. The package should be as follows,
```python
{
    "type": "stop",
    "name":"id-of-the-song"
}
```

3. \<QUEUE\>: This is a TCP package which contains the URL and title for the song. When this package is sent, receiver starts downloading the music with "pytube" library.

```python
{
    "type":"add",
    "action":"add/remove",
    "title":"\<title-to-be-displayed>"
}
```

4. \<DOWNLOAD\>: This is a TCP package which contains the URL and title for the song. When this package is sent, receiver starts downloading the music with "pytube" library.

```python
{
    "type":"download",
    "link":"<link-of-song>"
}
```

5. \<DISCOVERY\>: Discovery feature has the same mechanism that is implemented in class. UDP hello packet is recurrently sent to discover online users and expect receivers to send TCP "aleykumselam" packet.

```python
{
    "type":"hello",
    "name":"<name-of-sender>"
}

{
    "type":"aleykumselam",
    "name":"<name-of-receiver>"	
}
```

6. \<SYNC\>: This is a TCP package. This mechanism is required to sync the clocks of clients, and it is described in the previous section.

```python
{
	"type":"sync",
 	"timestamp":<time.time_ns()>+DELAY
}
```

## System Requirements
1. User should be able to see online users
1. User should be able to see connected users
1. User should be able to see the available musics in queue
1. User should be able to change the volume of music
1. User should be able to start music
1. User should be able to stop music
1. User should be able to change music
1. User should be able to add new music to queue
1. System should start the music in all connected devices
1. System should stop the music in all connected devices
1. System should change the music in all connected devices
1. System should add the new music in all connected devices
1. System should display available musics on cold start
1. System should retrieve the music URLs from YouTube API
1. System should have an UI