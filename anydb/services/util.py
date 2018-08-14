from cfoundation import Service
import socket, errno, os, shutil

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

    def get_parg(self, parg, default=None):
        pargs = self.app.pargs
        value = default
        if getattr(pargs, parg):
            value = getattr(pargs, parg)
        return value

    def rm_contents(self, path):
        for filename in os.listdir(path):
            full_path = os.path.join(path, filename)
            if os.path.isfile(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)
