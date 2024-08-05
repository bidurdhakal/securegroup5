
# Online Chat Application

## Introduction

'Online-chat' is a browser-based web chat application utilizing layer 7 protocols, specifically WebSocket. The WebSocket protocol facilitates end-to-end messaging between two clients over a network, offering a reliable full-duplex communication channel over TCP. This enables real-time communication between the client and server, supporting the following features:

- User login
- List of online users
- Private messaging between users
- Group (broadcast) messages to all online users
- Peer-to-peer file transfer

# Student Details

- Pemba Sherpa (a1905524)
- Saurab Kharel (a1919868)
- Roshan Bajracharya (a1941176)
- Bidur Dhakal (a1908335)

# Github Branches

If you want the first submission of code without peer review changes and with backdoors please clone the main branch
```sh
git clone https://github.com/bidurdhakal/securegroup5.git
```

But you want the second submission of code with peer review changes and remove of backdoors please clone the feedback_code branch
```sh
git clone -b feedback_code https://github.com/bidurdhakal/securegroup5.git
```

## Technologies Used

The application is developed with Python for server-side scripting, and JavaScript and HTML for the client-side. This combination ensures the application is resource-efficient and user-friendly.

## Prerequisites

To run this application, the following dependencies and scripts are required:

1. Download the `server.py` script.
2. Ensure all clients are on the same subnet or connected via a hotspot for testing.

### Server-side Prerequisites

#### Installing Python

For Linux, use the following commands to install the required dependencies:
```sh
apt update
apt install python3.8 python3.8-venv python3.8-dev
```

For Windows:
1. Download the Python installer from the official [Python website](https://www.python.org/downloads/).
2. Run the installer and ensure the path is correctly defined by checking the "*Add Python to PATH*" option.

For macOS:
```sh
brew update
brew install python@3.8
```

Install the necessary Python libraries:
```sh
pip install websockets
pip install python-dotenv
pip install bleach
```

After successfully installing all dependencies, configure the IP address and domain on the server side.

### Client-side Prerequisites

Download the client scripts. No additional dependencies are required for the client side.

## Configuration Changes

### Server-side Configuration

Create the `.env` file and add your IP address and port number respectively. 

![Server Output](./assets/envconfig.png)

After making the necessary changes, run the script:
```sh
python server.py
```
You should see output indicating that your IP address is associated with port 5555.

### Client-side Configuration

Download the `index.html`. Please use the same IP and port mentioned in . env file and changed in `script.js`. For example (ws://ip:port). Changed the IP and port on line number 11 on script.js.

![Server Output](./assets/js-change-ip.png)

To find your IP address, use `ipconfig` for Windows or `ifconfig` for Linux, and update it in the script accordingly.

Double-click on the `index.html` file to open it.

![Client Configuration](./assets/login.png)

We have created some test users with admin privilege. The index page will prompt for a jid and password for login. Use the following credentials:
```sh
Username: test1@s5
Password: test1@s5
```
```sh
Username: test2@s5
Password: test2@s5
```

After logging in, the main chat room will appear, showing the online users. In the example below, the users `test1` and `test2` are online.

![Test 1 Dashboard](./assets/test1-dashboard.png)

![Test 2 Dashboard](./assets/test2-dashboard.png)

The online chat between two clients is displayed as follows:

![Test1 Send Message](./assets/test1-send-message.png)

Test 1 sent message to Test 2
![Test2 Receive Message](./assets/test2-receive-message.png)
Test 2 received message from Test 1

### Some Screenshots of Group Chat
To start group chat we need to click on Group Chat 
![Group Chat started from Test1](./assets/group-chat-1.png)
![Group Chat started from Test1](./assets/group-chat-2.png)

This documentation provides a comprehensive guide to setting up and using the 'Online-chat' application, ensuring a seamless and secure communication experience.