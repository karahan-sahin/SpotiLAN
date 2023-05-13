import streamlit as st
import threading
import socket


def streamlit_thread():
    # Streamlit app code
    st.title("Streamlit App")
    # ...


def tcp_listener_thread():
    # TCP listener code
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)

    while True:
        client_socket, address = server_socket.accept()
        # Handle incoming TCP connections or messages as needed
        pass


# Create and start the Streamlit thread
streamlit_thread = threading.Thread(target=streamlit_thread)
streamlit_thread.start()

# Create and start the TCP listener thread
tcp_listener_thread = threading.Thread(target=tcp_listener_thread)
tcp_listener_thread.start()

# Wait for both threads to finish
streamlit_thread.join()
tcp_listener_thread.join()
