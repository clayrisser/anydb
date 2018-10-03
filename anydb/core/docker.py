from pydash import _
from sarge import run
import docker
import re

client = docker.from_env()

class Docker():
    def __init__(self, log=None):
        self.log = log

    def run(self, image, config={}, cmd=None):
        log = self.log
        command = self.create_command('docker run', config) + ' ' + image
        if cmd:
            command = command + ' ' + cmd
        log.debug('command: ' + command)
        run(command)

    def create_command(self, command, config):
        def each(value, key):
            nonlocal command
            key = '--' + key
            if key == '--port':
                key = '-p'
            if key == '--daemon':
                key = '-d'
            if isinstance(value, list):
                def each(value):
                    nonlocal key, command
                    if isinstance(value, bool):
                        if value:
                            command = command + ' ' + key
                    else:
                        command = command + ' ' + key + ' "' + value + '"'
                _.for_each(value, each)
            else:
                if isinstance(value, bool):
                    if value:
                        command = command + ' ' + key
                else:
                    command = command + ' ' + key + ' "' + value + '"'
        _.for_each(config, each)
        return command

    def get_containers(self, name=None, database=None):
        if name:
            if not len(re.findall(r'^anydb_', name)):
                if database and not len(re.findall(r'^anydb_' + database + '_', name)):
                    name = 'anydb_' + database + name
                else:
                    name = 'anydb_' + name
        else:
            if database:
                name = 'anydb_' + database + '_'
            else:
                name = 'anydb_'
        def filter_(value):
            if len(re.findall(r'^' + name, value.name)):
                return True
            return False
        return _.filter_(client.containers.list(all=True), filter_)

    def get_container(self, name=None, database=None):
        containers = self.get_containers(name, database)
        if not len(containers):
            return None
        return containers[0]

    def start(self, name, config={}, daemon=False):
        log = self.log
        command = self.create_command('docker start', config) + ' ' + name
        log.debug('command: ' + command)
        run(command)
        if not daemon:
            command = 'docker logs --tail 100 -f ' + name
            log.debug('command: ' + command)
            run(command)
