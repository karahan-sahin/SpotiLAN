import streamlit as st
from pytube import Search
from streamlit_player import st_player, _SUPPORTED_EVENTS



class SpotiLAN():
    
    ###########################
    # Overall TODOs
    # BUG: Fix playlist add/delete error
    # TODO: User discovery component
    # TODO: Add user login / ip detection
    ###########################
    
    def __init__(self) -> None:
        
        self.name = "Karahan"
        self.ip = "192.168.1.82"
        
        self.initSession()
        self.addStyle()

        self.event = None
        self.playList = []

    ###########################
    # INITIAL COMPONENTS/EVENTS
    ###########################

    def initSession(self):
        if 'URL' not in st.session_state:
            st.session_state['URL'] = "https://youtu.be/CmSKVW1v0xM"

        if 'ISCONTINUED' not in st.session_state:
            st.session_state['ISCONTINUED'] = True

        if 'CURRENT_TIME' not in st.session_state:
            st.session_state['CURRENT_TIME'] = 0

        if 'SEARCH_RESULT' not in st.session_state:
            st.session_state['SEARCH_RESULT'] = {}
            
        if 'CURRENT_SEARCH' not in st.session_state:
            st.session_state['CURRENT_SEARCH'] = ""
            
        if 'PLAYLIST' not in st.session_state:
            st.session_state['PLAYLIST'] = []
            
    def addStyle(self):
        st.markdown("""
        <style>

            iframe {
                display: none
            }

            .egzxvld5 {
                align-self: flex-end;
            }
            .css-12w0qpk {
                flex: 1 1;
            }
            
            .css-1y4p8pa {
                padding: 6rem 1rem 1rem;
            }
            
            .css-1y4p8pa {
                max-width: 1000
            }
            
            footer {
                display:none
            }
        </style>
        """, unsafe_allow_html=True)

    ###########################
    # PLAYER COMPONENTS/EVENTS
    ###########################

    def startAction(self):
        if st.session_state['ISCONTINUED']:
            try:
                st.session_state['CURRENT_TIME'] = self.event.data["played"]
            except:
                pass

    def startstop(self, opt): st.session_state['ISCONTINUED'] = opt

    #############################
    # SEARCHBAR COMPONENTS/EVENTS
    #############################

    def onDelete(self, idx): st.session_state['PLAYLIST'].pop(idx)

    def urlChange(self, title, url): st.session_state['PLAYLIST'].append((title,url))

    def getSearchResults(self, query):
        st.session_state["CURRENT_SEARCH"] = query
        st.session_state['SEARCH_RESULT'] = {}
        s = Search(query)
        try:
            for v in s.results:
                st.session_state['SEARCH_RESULT'][v.title] = v.watch_url
                
        except:
            # TODO: Add error display
            print(" ** Your query is not able is not fetched ** ")
            pass

    def generateSearchBar(self):
        
        with st.sidebar:
            query = st.text_input("Search Song")
            if query != st.session_state["CURRENT_SEARCH"]:
                self.getSearchResults(query)
            
            with st.expander("Search Results"):
                for title, url in st.session_state['SEARCH_RESULT'].items():
                    col1, col2,  = st.columns([3,1])
                    col1.write(title)
                    col2.button(label="➕", key=url, on_click=self.urlChange(title,url))

    #############################
    # PLAYLIST COMPONENTS/EVENTS
    #############################

    def generatePlayer(self):
        
        for idx, (title, url) in enumerate(st.session_state['PLAYLIST']):
            col1, col2,  = st.columns([3,1])
            col1.write(title)
            col2.button("x", key=idx, on_click=self.onDelete(idx))
        
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.button("⏮️")
            if col2.button("▶"):
                self.startstop(True)
            if col3.button("⏸️"):
                self.startstop(False)
            col4.button("⏭️")

        options = { "events":  _SUPPORTED_EVENTS, "progress_interval": 100, "volume": 1, "height": 1, "playing": st.session_state['ISCONTINUED'] }

        self.event = st_player(st.session_state['URL'], **options, key="youtube_player")
        
        st.slider("Time",1,100, int(st.session_state['CURRENT_TIME']*100), label_visibility="collapsed")

    ###########################
    # FRIENDLIST COMPONENTS/EVENTS
    # TODO: Generate components
    ###########################
    
    def generateFriendList(self):
        with st.sidebar:
            col1, col2,  = st.columns([3,1])
            col1.write("User 1")
            col2.write("OFFLINE")
            
            col3, col4,  = st.columns([3,1])
            col3.write("User 2")
            col4.write("OFFLINE")

if __name__ == "__main__":
    
    app = SpotiLAN()
    
    app.generatePlayer()
    app.generateSearchBar()
    app.generateFriendList()