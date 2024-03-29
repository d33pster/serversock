# Overview
serversock is a python module to create a server that can accept connection from multiple clients at the same time using multithreading.

## Installation
serversock is listed in pypi so the installation is very simple

```bash
# in your terminal/CMD run

pip install serversock
```

## Usage

### Creating server

```python
# import package
from serversock.serversock import _server

# create class object
serverCTRL = _server(address, port, bufffsize)
```

The arguments of _server are defined below as

```python
class _server:
    def __init__(self, address:str, port: int, buffsize:int = 1024):
        """_server initialization

        Args:
            address (str): Enter Address like '0.0.0.0'
            port (int): Enter port number, example: 8080
            buffsize (int, optional): message buffsize. Defaults to 1024.
        """
        ...
    ...
```

After class object creation, start server
```python
# start server

serverCTRL._start(serverfilename, responses)
```

The arguments of _start are defined below as:
```python
class _server:
    ...
    def _start(self, serverfilename:str, responses:int = 1):
        """start server

        Args:
            serverfilename (str): serverfilename to save server data
            responses (int, optional): Number of response expected from client. Defaults to 1.
        """
        ...
    ...
```

### Creating clients
```python
# import _client class from serversock

from serversock.serversock import _client

# create class object
clientCTRL = _client(serveraddress, serverport, serverbufflimit)
```
The arguments of _client are defined below as:
```python
class _client:
    def __init__(self, serveraddress:str, serverport:int, serverbufflimit:int = 1024):
        """_client class initialization

        Args:
            serveraddress (str): server address like '0.0.0.0'
            serverport (int): server port like 8080
            serverbufflimit (int, optional): buffersize. Defaults to 1024.
        """
        ...
    ...
```

After that client can perform a bunch of tasks like send a message, sync with the server and disconnect voluntarily.

- send message and get response in return
    - client can send message to the server that the server will save.

    ```python
    # send message
    clientCTRL._sendToServer(message)
    ```
- sync with the server
    - the server sends the complete data that the server has stored to the client in the form of a string.
    ```python
    # sync with the server
    completedata = clientCTRL._refresh() # this will return a string.

    # to get the list of lines in the file, do completedata.split('\n')
    completedata = completedata.split('\n')
    ```
- disconnect voluntarily
    ```python
    # disconnect
    clientCTRL._disconnect()
    ```


## Terminal Controls

### Check version
```bash
# in terminal/CMD, run

serversock -v # or serversock --version
```
### Show help text
```bash
# in terminal/CMD run

serversock -h # or serversock --help
```

## Uninstallation

serversock can be uninstalled using pip

```bash
# uninstall

pip uninstall serversock
```