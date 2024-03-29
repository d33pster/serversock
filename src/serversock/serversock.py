#!/usr/bin/env python3

__version__ = '0.1'

from socket import socket as serversock, AF_INET, SOCK_STREAM
from threading import Thread, active_count as activethreads
from optioner import options
from platform import system as resolveos
from os import system as run, getcwd as pwd
from os.path import join, exists as there
from time import sleep
from sys import argv
from colorama import init as color, Fore as _

class _server:
    def __init__(self, address:str, port: int, buffsize:int = 1024):
        """_server initialization

        Args:
            address (str): Enter Address like '0.0.0.0'
            port (int): Enter port number, example: 8080
            buffsize (int, optional): message buffsize. Defaults to 1024.
        """
        # make server
        try:
            self.server = serversock(AF_INET, SOCK_STREAM)
        except Exception as e:
            print(f'MAKE-SERVER-ERROR: {e}')
        # bind server to address and port
        self.server.bind((address, port))
        
        # save current working directory where this class is called.
        self.directory = pwd()
        
        # save address and port and buffsize
        self.address = address
        self.port = port
        self.buff = buffsize
    
    def _start(self, serverfilename:str, responses:int = 1):
        """start server

        Args:
            serverfilename (str): serverfilename to save server data
            responses (int, optional): Number of response expected from server. Defaults to 1.
        """
        self.responses = responses
        self.filename = serverfilename
        try:
            # start listening
            self.server.listen()
            print(f'[server]->[{self.address}]:[{self.port}]')
            # run continuously and create threads for each connection.
            while True:
                self.connection, self.conaddress = self.server.accept()
                thread = Thread(target=self.handleclient)
                thread.start()
                print(f'\nConnected to {self.conaddress}')
                print(f'Active: {activethreads()-1}')
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print(f'SERVER-ERROR: {e}')

    def handleclient(self):
        try:
            # set connected to True
            connected = True
            # set resp to number of responses 
            resp = self.responses
            # while connected status is true
            while connected:
                # while number of responses are above 0
                while resp>0:
                    # recieve message
                    message = self.connection.recv(self.buff).decode()
                    # if message is recieved and it is not 'disconnect' or 'refresh' command instructions
                    if message and (message!='disconnect' or message!='refresh'):
                        # send back acknowledgement
                        self.connection.send('gotmessage'.encode())
                    # if message is recieved and message is disconnect command
                    elif message and message=='disconnect':
                        # send disconnect acknowledgement
                        self.connection.send('disconnect'.encode())
                        # close connection
                        self.connection.close()
                        # print status
                        print(f'[CONNECTION-TERMINATED-EXPLICITLY][{self.address}]')
                        # end function
                        return
                    # if message is recieved and message is refresh command
                    elif message and message=='refresh':
                        # if the serverfile exists
                        if there(join(self.directory, self.filename)):
                            # open serverfile in read mode
                            with open(join(self.directory, self.filename), 'r') as serverfile:
                                # read only upto buffsize provided by user
                                content = serverfile.read(self.buff)
                                # if server file is not empty and the above line read some content
                                while content:
                                    # send the content to client
                                    self.connection.send(content.encode())
                                    # update content with the next buffer of buffsize given by user
                                    content = serverfile.read(self.buff)
                                    # NOTE: the loop will only repeat if the serverfile has more content.
                                # send serverfile end acknowledgement
                                self.connection.send('done'.encode())
                            # close connection
                            self.connection.close()
                            # print status
                            print(f'[CONNECTION-TERMINATED-AFTER-REFRESH_REQUEST][{self.address}]')
                            # end function
                            return
                        # if serverfile doesn't exist
                        else:
                            # send error to client
                            self.connection.send('error:nofile'.encode())
                            # close connection
                            self.connection.close()
                            # print status
                            print(f'[CONNECTION-TERMINATED-SERVERFILE-NOTFOUND][{self.address}]')
                            # end function
                            return
                    # if no message recieved
                    else:
                        # re-run the loop
                        continue
                    
                    # if message is recieved and it is not any defined commands, open serverfile in append mode
                    with open(join(self.directory, self.filename), 'a') as serverfile:
                        # write the message
                        serverfile.write(message+"\n")
                    # update response count
                    resp -= 1
            # when responses reach limit, close the connection
            self.connection.close()
            # show status
            print(f'[CONNECTION-TERMINATED-RESPONSE-LIMIT-REACHED][{self.address}]')
        except ConnectionResetError:
            # print status
            print(f'[CONNECTION-TERMINATED-BY-CLIENT][{self.address}]')

class _client:
    def __init__(self, serveraddress:str, serverport:int, serverbufflimit:int = 1024):
        """_client class initialization

        Args:
            serveraddress (str): server address like '0.0.0.0'
            serverport (int): server port like 8080
            serverbufflimit (int, optional): buffersize. Defaults to 1024.
        """
        # make client
        self.client = serversock(AF_INET, SOCK_STREAM)
        # save address and port
        self.address = serveraddress
        self.port = serverport
        # save buffsize
        self.buff = serverbufflimit
    
    def reinit(self):
        self.client = serversock(AF_INET, SOCK_STREAM)
    
    def divide(self, message:str) -> list[str]:
        # define a list
        divided = []
        # for i = 0 to len(message) with step = buffsize 
        for i in range(0, len(message), self.buff):
            # append an element as a string -> message[from i to (i+buffsize)]
            divided.append(message[i:i+self.buff])
        # return list[str]
        return divided
    
    def _sendToServer(self, message:str):
        """send message to server

        Args:
            message (str): message to be sent to server
        """
        # connect to server
        self.client.connect((self.address, self.port))
        # if message is shorter than buffsize
        if len(message)<=self.buff:
            # send client the message
            self.client.send(message.encode())
            # if acknowledgement is recieved
            if self.client.recv(self.buff).decode() == 'gotmessage':
                # close the connection
                self.client.close()
            # if acknowledgement not recieved
            else:
                # print error
                print(f'[ACKNOWLEDGEMENT-ERROR]')
        # if message is longer than buffsize
        else:
            # divide message into chunks of size<=buffsize
            messages = self.divide(message)
            # for each chunk, send the message every 7 second for the server to respond and acknowledge
            for msg in messages:
                # use recursion to send the message
                self._sendToServer(msg)
                # sleep 7 sec
                sleep(7)
        
        # reinit
        self.reinit()
    
    def _refresh(self) -> str:
        """synchronize your data with the server

        Returns:
            str: the whole data from server is returned as a string.
            NOTE: if can split it by '\n' to get each line in the resulting list.
        """
        # connect to server
        self.client.connect((self.address, self.port))
        # send refresh command
        self.client.send('refresh'.encode())
        # define content
        content = ''
        # while acknowledgement is not recieved
        chunk = self.client.recv(self.buff).decode()
        while chunk != 'done':
            content += chunk
            chunk = self.client.recv(self.buff).decode()
        
        # close the connection
        self.client.close()
        
        # reinit
        self.reinit()
        
        # return content
        return content
    
    def _disconnect(self):
        """disconnect client from server
        """
        # connect to server
        self.client.connect((self.address, self.port))
        # send disconnect command
        self.client.send('disconnect'.encode())
        # if acknowledgement recieved
        if self.client.recv(self.buff).decode() == 'disconnect':
            print(f'[SERVER-DISCONNECT-EXPLICITLY-BY-CLIENT][{self.address}]')
        else:
            print(f'[DISCONNECT-ERROR][{self.address}]')
            # close yourself
            self.client.close()
        
        self.reinit()

def main():
    color()
    # define arguments
    shortargs = ['h', 'v', 's', 'c']
    longargs = ['help', 'version', 'server', 'client']
    ifthisthennotthat = [['s', 'server'], ['c', 'client']]
    
    optCTRL = options(shortargs, longargs, argv[1:], ifthisthennotthat=ifthisthennotthat)

    actualargs, check, error, falseargs = optCTRL._argparse()
    
    if not check:
        print(f'ERROR: {error}')
    else:
        if '-h' in actualargs or '--help' in actualargs:
            helper()
        elif '-v' in actualargs or '--version' in actualargs:
            version()
        elif '-s' in actualargs or '--server' in actualargs:
            # server()
            pass
        elif '-c' in actualargs or '--client' in actualargs:
            # client()
            pass
        else:
            print(f'ERROR: No argument Provided')

def version():
    print(f'{_.BLUE}serversock{_.RESET} copyright Soumyo Deep Gupta 2024')
    print(f'version {_.RED}v{__version__}{_.RESET}')
    exit(0)

def helper():
    print(f'{_.BLUE}serversock{_.RESET} - {_.YELLOW}help text{_.RESET}\n')
    print(f'   |   -h or --help        : show this help text and exit.')
    print(f'   |   -v or --version     : show version info and exit.')
    print(f'   |   -s or --server      : server mode. (coming soon)')
    print(f'   |   -c or --client      : client mode (coming soon)')
    print(f'NOTE: server and client arguments are mutually exclusive.')
    print('END')
    exit(0)

# def server():

if __name__=='__main__':
    main()