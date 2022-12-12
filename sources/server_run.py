import Server

server = Server.Server(('localhost', 8070))
server.start()
server.handle_client()