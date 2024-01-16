from websocket_server import WebsocketServer
import sys
import threading
import time
import os
import fcntl
import select


sshim_client = None

# Called for every client connecting (after handshake)
def new_client(client, server):
        global sshim_client
        if (sshim_client == None):
                sshim_client = client

# Called for every client disconnecting
def client_left(client, server):
        global sshim_client
        sshim_client = None

# Called when a client sends a message
def message_received(client, server, message):
        sys.stdout.buffer.write(message)
        sys.stdout.buffer.flush()

def thread_input(server):
        global sshim_client
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)
        while True:
                if sshim_client != None:
                        break
                else:
                        time.sleep(4)
        while True:
            i = [sys.stdin]
            ins, _, _  = select.select(i, [], [], 0)
            if len(ins) != 0:
                    data = sys.stdin.buffer.read()                    
                    server.send_message_to_all(data)


PORT=9001
server = WebsocketServer(port = PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)


x = threading.Thread(target=thread_input, args=(server,))
x.start()

server.run_forever()
