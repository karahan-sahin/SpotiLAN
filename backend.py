import os
import json
import time
import pyDes
import random
import socket
import threading
from ast import literal_eval
from collections import defaultdict


import hashlib


PORT = 12345
BUFFERSIZE = 1024

class Backend():
    
    ###########################
    # Overall TODOs
    # TODO: Implement Sync Module
    # TODO: Add user login / ip detection
    # TODO: Add packet types
    # TODO: Add connector modules with frond-end
    # TODO: Add cache cleaning 
    ###########################
        
    
    def __init__(self, name) -> None:
        
        self.ip = ""
        self.name = name
        
        self.persons = defaultdict(dict) # ip -> name
        self.persons_lock = threading.Lock()
        self.ttl = defaultdict(dict) # ip -> time
        self.ttl_lock = threading.Lock()
        self.ips = defaultdict(dict) # name -> ip
        self.ips_lock = threading.Lock()
                     
        self.startThread()
       
    #############
    #  SYNCING
    #############

    def createCountdown(self, seq):
        for seq in range(1,10):
            self.broadcast_send(json.dumps({
                "type":"countdown",
                "seq": seq,
                "timestamp":time.perftime()
            }))


    #############
    #  DISCOVER
    #############
    
    def broadcast_send(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('',0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
            s.sendto(msg.encode('UTF-8'), ('<broadcast>', PORT))    

    def discover_nodes(self):
        print("Started node discovery...")
        hello_msg = json.dumps({ "type": "hello", "myname": self.name})
        # Discover for ever
        while True:
            self.broadcast_send(hello_msg)
            time.sleep(10)

    #############
    #  RECIEVER
    #############
    
    def recv_parser(self, fmsg, ip):
        
        fmsg = json.loads(fmsg) 
               
        # Discovery message type
        if fmsg["type"] == "hello":
            name = fmsg["myname"].strip()
            with self.ttl_lock: self.ttl[ip] = time.time()
            # Prevent double addition, person already added
            with self.persons_lock:
                if ip in self.persons.keys():
                    return
                self.persons[ip]["name"] = name
            with self.ips_lock: self.ips[name] = ip
            print(name, "with ip", ip, "joined.")
            hello_msg = json.dumps({"type": "aleykumselam", "myname": self.name})
            self.socket_send(ip, hello_msg)
            self.sendInit(ip)
            
        # Reply message type
        elif fmsg["type"] == "aleykumselam":
            name = fmsg["myname"].strip()
            with self.ttl_lock: self.ttl[ip] = time.time()
            # Prevent double addition, person already added
            with self.persons_lock:
                if ip in self.persons.keys():
                    return
                self.persons[ip]["name"] = name
            with self.ips_lock: self.ips[name] = ip
            print(name, "with ip", ip, "joined.")
            
        elif fmsg["type"] == "<START>": pass # START CURRENT SONG
        elif fmsg["type"] == "<STOP>": pass # STOP CURRENT SONG
        elif fmsg["type"] == "<CHANGE>": pass # CHANGE SONG AT PLAYLIST
        elif fmsg["type"] == "<ADD>": pass # ADD SONGS TO PLAYLIST

        else:
            print("(???) Unresolved message -", fmsg)

    def recv_broadcast(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', PORT))
            while True:
                data, addr = s.recvfrom(1024)
                if(addr[0] == self.ip):
                    continue
                threading.Thread(target=self.recv_parser, args=(data.decode('UTF-8'), addr[0]), daemon=True).start()

    def recv_msg(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, PORT))
            while True:
                # Check port for any incoming message
                s.listen()
                conn, addr = s.accept()
                fmsg=""
                try:
                    with conn:
                        while True:
                            data = conn.recv(BUFFERSIZE)
                            if not data:
                                break
                            fmsg+=data.decode('UTF-8')
                    threading.Thread(target=self.recv_parser, args=(fmsg, addr[0]), daemon=True).start()
                except Exception as e:
                    print("Error receiving message from",addr, ":", e)
                    pass

    ###########
    #  SENDER
    ###########

    def socket_send(self, host, msg):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, PORT))
                s.sendall(msg.encode('UTF-8'))
        except Exception as e:
            return False
        return True

    def send_msg(self, ip, msg):        
        content_msg = json.dumps({"type": "message", "content": str(self.encodeMsg(msg))})
        self.socket_send(ip, content_msg)
    
    def startThread(self):
        # Start listening to port
        read_thread = threading.Thread(target=self.recv_msg, daemon=True)
        read_thread.start()

        # Get greeting from other peers
        broadcast_thread = threading.Thread(target=self.recv_broadcast, daemon=True)
        broadcast_thread.start()

        # Discover other peers
        discover_thread = threading.Thread(target=self.discover_nodes, daemon=True)
        discover_thread.start()

        # Periodic cleanup service
        #cleanup_thread = threading.Thread(target=cleanup_service, daemon=True)
        #cleanup_thread.start()