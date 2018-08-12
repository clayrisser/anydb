from cfoundation import Service
import socket, errno

class Util(Service):
    def get_port(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('127.0.0.1', port))
        except socket.error as err:
            if err.errno == errno.EADDRINUSE:
                port = self.get_port(port + 1)
        s.close()
        return port
