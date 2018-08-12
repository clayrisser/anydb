from cfoundation import Service
from os import path
from sarge import run
from subprocess import Popen, PIPE
from sys import stdout
import pydash as _

class Docker(Service):
    def run(self, image, config={}, cmd=None):
        s = self.app.services
        log = self.app.log
        command = self.create_command('docker run', config) + ' ' + image
        if cmd:
            command = command + ' "' + cmd + '"'
        log.debug('command: ' + command)
        run(command)

    def start(self, name, config={}):
        s = self.app.services
        log = self.app.log
        command = self.create_command('docker start', config) + ' ' + name
        log.debug('command: ' + command)
        run(command)

    def create_command(self, command, config):
        def each(value, key):
            nonlocal command
            key = '--' + key
            if key == '--port':
                key = '-p'
            if isinstance(value, list):
                def each(value):
                    nonlocal key, command
                    command = command + ' ' + key + ' "' + value + '"'
                _.for_each(value, each)
            else:
                command = command + ' ' + key + ' "' + value + '"'
        _.for_each(config, each)
        return command
