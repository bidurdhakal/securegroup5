"""
This module uses the following libraries:
- `asyncio`: Provides support for asynchronous I/O operations.
- `websockets`: Handles WebSocket connections and communication.
- `json`: Manages JSON.
- `bcrypt`: Handles password hashing.
"""

import asyncio
import json
import os
import websockets
import bcrypt
import bleach
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

def verify_password(stored_hash, provided_password):
    """
    checks if the provided password matches the stored hashed password.
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash)


# Registered Clients
registered_clients = {
    "c1@s5": {
        "nickname": "pemba",
        "jid": "c1@s5",
        "password": b'$2b$12$qWoDtedvx8jurr/2XVex7.raoa7tqIofxPYrx1.oy6qmDpHavkYwa',
    },
    "c2@s5": {
        "nickname": "saurab",
        "jid": "c2@s5",
        "password": b'$2b$12$suJThyymiIVez4nLyUjpPurPq/E3BBTRdDGMnxADdbIjdst5kbKvS'
    },
    "c3@s5": {
        "nickname": "roshan",
        "jid": "c3@s5",
        "password": b'$2b$12$Cz8bUuhzYyoHMdbvZLlcs.Cc0nOSR3VzAHOFrnF3ic6unrxZ6rwoG'
    },
    "c4@s5": {
        "nickname": "bidur",
        "jid": "c4@s5",
        "password": b'$2b$12$FwNWm33zvTOFtK6yrUXW0uMrMdu9jGR9AY7RgKgcm0sEzWjbhquOK'
    },
    "test1@s5": {
        "nickname": "test1",
        "jid": "test1@s5",
        "password": b'$2b$12$JMN7bSNLOQw9CvefBs79rOsQYefOhnFfxt1zzKVsiKF1tw7ha5URG',
    },
    "test2@s5": {
        "nickname": "test2",
        "jid": "test2@s5",
        "password": b'$2b$12$rFzKEMeiJISlYvU1CMzSg.8ZdUn3vbfKtBRBmjQuJ3vpQV5zOY12u'
    },
}

# Store active clients
active_connections = {}
ip = os.getenv('IP')
port = os.getenv('PORT')


async def handle_client(websocket,path):
    """
    Responsible for communicating with clients
    """
    jid = None
    try:
        data = await receive_data(websocket)
        jid = bleach.clean(data['presence'][0].get('jid'))
        password = bleach.clean(data['presence'][0].get('password'))
        publickey = data['presence'][0].get('publickey')

        # input validation and protecting input from buffer overflow
        if not jid:
            await send_error(websocket, "* JID cannot be empty")


        elif len(jid) > 64:
            await send_error(websocket, '* JID should be less than 64 characters')

        elif password == '':
            await send_error(websocket,"* Password cannot be empty")

        elif len(password) > 64:
            await send_error(websocket, '* Password should be less than 64 characters')

        elif authenticate_user(jid, password):
            # if user is authenticated add users to active connections
            current_user = add_clients_to_active_connections(jid, websocket, publickey)
            # once client is logged in successfully
            await send_login_success(websocket, current_user)
            # broadcast presence to all the clients
            await broadcast_presence()
            await handle_messages(websocket)
        else:
            # broadcast error message to specific client
            await send_error(websocket, "Incorrect email and password")

    except websockets.exceptions.ConnectionClosedError as e:
        # if server is disconnected
        print(f"Connection closed with error code {e}")

    finally:
        # if disconnect remove users from active connections
        await cleanup_user(jid)
        await asyncio.sleep(5)  # Wait before trying to reconnect
        await attempt_reconnect()

async def attempt_reconnect():
    """
    Attempt to reconnect if the connection is closed.
    """
    print("Attempting to reconnect...")
    try:
        async with websockets.connect(f"ws://{ip}:{port}") as websocket: # pylint: disable=no-member
            await handle_client(websocket)

    except Exception as e: # pylint: disable=broad-except
        print(f"Reconnection failed with error: {e}")
        await asyncio.sleep(5)


async def receive_data(websocket):
    """
        Reads a message from the WebSocket connection.
    """
    response = await websocket.recv()
    return json.loads(response)


def authenticate_user(jid, password):
    """
    Checks if the user is authenticated
    """
    if jid in registered_clients:
        user = registered_clients[jid]
        return verify_password(user['password'], password)
    return False


def add_clients_to_active_connections(jid, websocket, publickey):
    """
    add clients to active connections
    """
    user = registered_clients[jid]
    user['websocket'] = websocket
    user['publickey'] = publickey
    active_connections[jid] = user
    return user


async def send_login_success(websocket, user):
    """
    broadcast login message to client
    """
    success_message = {
        "tag": "success",
        "message": "Login successful",
        "nickname": user['nickname']
    }
    await send_message(websocket, success_message)


async def send_error(websocket, message):
    """
    broadcast error message to client
    """
    error_message = {
        "tag": "error",
        "message": message
    }
    await send_message(websocket, error_message)


#
async def handle_messages(websocket):
    """
    it handles when clients send message to other client or public
    """
    async for message in websocket:
        data = json.loads(message)
        await process_message(data)


async def process_message(data):
    """
    it forwards the message to specific client or public
    """
    if data.get('from') in active_connections:
        target_jid = data.get('to')
        info = bleach.clean(data.get('info'))
        if data.get('tag') == 'message' and info:
            message_format = create_message_format(data, tag='message')
            await route_message(target_jid, message_format)
        elif data.get('tag') == 'file':
            file_message = create_message_format(data, tag='file')
            await route_message(target_jid, file_message)
        else:
            print('Invalid or incomplete message format')
    else:
        print('Sender is not active')


def create_message_format(data, tag):
    """
    message format if file or text
    """
    message = {
        "tag": tag,
        "from": data.get('from'),
        "to": data.get('to'),
        "info": data.get('info'),
    }
    if tag == 'file':
        message["filename"] = data.get('filename')
    return message


async def route_message(target_jid, message):
    """
    it handles whether to send to msg to specific client or public
    """
    if target_jid == 'public':
        await broadcast(message)
    elif target_jid in active_connections:
        await send_message(active_connections[target_jid]['websocket'], message)
    else:
        print('Target client is not active')


async def broadcast(message):
    """
    broadcast any message to all the clients
    """
    for client_info in active_connections.values():
        await send_message(client_info['websocket'], message)


async def broadcast_presence():
    """
     broadcast online presence to all users
    """
    online_users = {
        "tag": "presence",
        "presence": [
            {
                "nickname": client_info.get('nickname'),
                "jid": client_info.get('jid'),
                "publickey": client_info.get('publickey')
            } for client_info in active_connections.values()
        ]
    }
    await broadcast(online_users)


async def send_message(websocket, message):
    """
     send message to client web socket
    """
    await websocket.send(json.dumps(message))


async def cleanup_user(jid):
    """
    delete the user from active connections and broadcast new presence to all users
    """
    if jid in active_connections:
        del active_connections[jid]
        await broadcast_presence()


async def main():
    """
    Start the websocket server
    """
    server = await websockets.serve(handle_client, ip, port) # pylint: disable=no-member
    print(f"WebSocket server started at ws://{ip}:{port}")
    await server.wait_closed()

# Run server forever
if __name__ == "__main__":
    asyncio.run(main())
