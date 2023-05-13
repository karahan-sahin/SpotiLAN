import subprocess
import re
from typing import Dict
import threading
import platform


class Client:
    """Client class contains the users private IP address, name and known hosts as attributes"""

    def __init__(self, myname: str = None, myip: str = None):
        self.__ip: str = myip if myip is not None else Client.__get_private_ip__()
        self.__name: str = myname
        self.__known_hosts: dict = dict()
        self.lock: threading.Lock = threading.Lock()

    @property
    def myip(self) -> str:
        """
        Getter method for myip attribute
        """
        return self.__ip

    @property
    def myname(self) -> str:
        """
        Getter method for myname attribute
        """
        return self.__name

    @property
    def known_hosts(self) -> dict:
        """
        Getter method for known hosts attribute
        """
        return self.__known_hosts

    @property
    def me(self) -> dict:
        """
        Getter method for self introduction dictionary
        """
        return self.__identify_yourself__()

    def __identify_yourself__(self, ) -> Dict[str, str]:
        """
        Private method for generating self introduction dict
        :return: self introduction dict
        """
        params = {"type": "hello", "myname": self.myname}
        return params

    def add_known_host(self, ip: str, name: str) -> None:
        """
        Compares known hosts with other host, adds the other if not met yet
        :param ip: private ip of the host
        :param name: name of the host
        """
        if self.__known_hosts.get(name) == ip:
            return
        self.__known_hosts[name] = ip
        print(f'Known hosts are {list(self.known_hosts.keys())}')

    def clear_known_hosts(self) -> None:
        """
        Clear the known hosts dict
        """
        self.__known_hosts = dict()

    @staticmethod
    def __get_private_ip__() -> str:
        """
        Gets the clients private IP address, by utilizing ifconfig command with subprocess module
        :return: Private IP as str
        """
        try:
            # Check if the operating system is Windows
            if platform.system() == "Windows":
                import socket
                print("The operating system is Windows")
                # Get the hostname of the local machine
                hostname = socket.gethostname()

                # Get a list of IP addresses associated with the hostname
                ip_addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_IP,
                                                  socket.AI_PASSIVE)
                ip_address = ip_addresses[0][4][0]

                print(f"My private IP address is: {ip_address}")
                return ip_address

            print("The operating system is not Windows")
            # Run ifconfig command to get network interface information
            output = subprocess.check_output(['ifconfig'])

            # Convert output to string
            output_str = output.decode('utf-8')

            # Use regex to find IP address
            match = re.search(r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output_str)
            # Get the IP address if found
            if match:
                private_ip = match.group(1)
                print(f"My private IP address is: {private_ip}")
                return private_ip
            else:
                raise Exception("Could not find private IP address")
        except Exception as e:
            raise e

    def __eq__(self, other) -> bool:
        """
        Overrides __eq__ method
        """
        if isinstance(other, Client):
            return self.myname == other.myname and self.myip == other.myip
        return False

    def __repr__(self) -> str:
        """
        Overrides __repr__ method
        """
        return f'Identity(\'{self.myip}\', {self.myname})'
