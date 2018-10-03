from . import Docker
from .util import rm_contents
from distutils.dir_util import copy_tree
from pydash import _
from time import sleep
import os

class MongoService():
    def __init__(self, name=None, log=None, options={}):
        self.name = name
        self.log = log
        self.options = options

    def start(self):
        log = self.log
        name = self.name
        log.info('starting mongo database \'' + name + '\'')
        docker = Docker(log=log)
        options = self.options
        container = docker.get_container(name)
        if not container:
            os.makedirs(options.paths.volumes.data)
            os.makedirs(options.paths.volumes.restore)
            docker.run('mongo', {
                'daemon': True,
                'name': name,
                'port': options.port,
                'volume': options.volumes
            })
        if options.reset:
            self.reset()
        if options.paths.restore:
            self.restore()
        if options.rename:
            self.rename()
        return docker.start(name, {}, daemon=options.daemon)

    def stop(self):
        log = self.log
        name = self.name
        log.info('stopping mongo database \'' + name + '\'')
        docker = Docker(log=log)
        docker.stop_container(name)

    def restore(self):
        log = self.log
        name = self.name
        log.info('restoring mongo database \'' + name + '\'')
        docker = Docker(log=log)
        options = self.options
        container = docker.get_container(name)
        if not container:
            log.warning('\'' + name + '\' does not exist')
            return None
        exited = False
        if container.status == 'exited':
            exited = True
            docker.start(name, {}, daemon=True)
        if os.path.exists(options.paths.restore) and os.path.isdir(options.paths.restore):
            copy_tree(
                options.paths.restore,
                options.paths.volumes.restore
            )
        log.info('waiting 10 seconds')
        sleep(10)
        docker.execute(name, {}, '/usr/bin/mongorestore /restore')
        if os.path.exists(options.paths.volumes.restore):
            rm_contents(options.paths.volumes.restore)
        if exited:
            self.stop()

    def reset(self):
        pass

    def rename(self):
        pass

    def remove(self, name=None):
        log = self.log
        name = name if name else self.name
        log.info('removing mongo database \'' + name + '\'')
        docker = Docker(log=log)
        docker.remove_container(name)

    def list(self):
        log = self.log
        docker = Docker(log=log)
        containers = docker.get_containers(database='mongo')
        log.info(_.map_(containers, lambda container: container.name))

    def nuke(self):
        log = self.log
        docker = Docker(log=log)
        containers = docker.get_containers(database='mongo')
        def each(container):
            self.remove(container.name)
        _.for_each(containers, each)
