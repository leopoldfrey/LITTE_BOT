from websocket_server import WebsocketServer
import time

def new_client(client, server):
	server.send_message(client,'Hi')

def msg_received(client, server, mess):
	print('Mess',mess)

server = WebsocketServer(port=4446, host='127.0.0.1')
server.set_fn_new_client(new_client)
server.set_fn_message_received(msg_received)
server.run_forever()
