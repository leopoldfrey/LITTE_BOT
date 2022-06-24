from pyosc import Client, Server

def oscIn(address, *args):
    print("[Server] OSC IN ", address, args[0])

osc_server = Server('0.0.0.0', 14000, oscIn)
