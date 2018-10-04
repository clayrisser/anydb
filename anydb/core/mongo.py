from . import Docker
from .util import rm_contents
from distutils.dir_util import copy_tree
from halo import Halo
from munch import munchify
from pydash import _
from time import sleep
import os, shutil

spinner = Halo(spinner='dots')

class MongoService():
    def __init__(self, name=None, log=None, options={}):
        self.name = name
        self.log = log
        self.options = options

    def start(self, silent=False, daemon=None):
        log = self.log
        name = self.name
        options = self.options
        if silent:
            daemon = True
        if daemon == None and 'daemon' in options and options.daemon:
            daemon = options.daemon
        if not silent:
            spinner.start('starting mongo database \'' + name + '\'')
        docker = Docker(log=log)
        container = docker.get_container(name)
        if not container:
            if not os.path.exists(options.paths.volumes.data):
                os.makedirs(options.paths.volumes.data)
            if not os.path.exists(options.paths.volumes.restore):
                os.makedirs(options.paths.volumes.restore)
            self.reset(silent=True)
            docker.run('mongo', munchify({
                'daemon': True,
                'name': name,
                'port': options.port,
                'volume': options.volumes
            }))
        if 'reset' in options and options.reset:
            self.reset()
        if 'restore' in options.paths:
            self.restore(preserve_exit=False)
        if options.rename:
            self.rename()
        if not silent:
            if daemon:
                spinner.succeed('started mongo database \'' + name + '\'')
            else:
                spinner.stop()
        return docker.start(name, {}, daemon=daemon)

    def stop(self, name=None, silent=False):
        log = self.log
        name = name if name else self.name
        if not silent:
            spinner.start('stopping mongo database \'' + name + '\'')
        docker = Docker(log=log)
        docker.stop_container(name)
        if not silent:
            spinner.succeed('stopped mongo database \'' + name + '\'')

    def reset(self, silent=False):
        log = self.log
        name = self.name
        options = self.options
        if not silent:
            spinner.start('resetting mongo database \'' + name + '\'')
        docker = Docker(log=log)
        docker.run('busybox', munchify({
            'daemon': False,
            'rm': True,
            'volume': [
                options.paths.volumes.data + ':/data',
                options.paths.volumes.restore + ':/restore'
            ]
        }), 'sh -c "rm -rf /data/* /data/.* /restore/* /restore/.* 2>/dev/null || true"')
        if not silent:
            spinner.succeed('reset mongo database \'' + name + '\'')

    def remove(self, name=None, silent=None):
        log = self.log
        name = name if name else self.name
        if not silent:
            spinner.start('removing mongo database \'' + name + '\'')
        docker = Docker(log=log)
        container = docker.get_container(name)
        if container.status != 'exited':
            self.stop(name)
        docker.remove_container(name)
        if not silent:
            spinner.succeed('removed mongo database \'' + name + '\'')

    def nuke(self, silent=False):
        log = self.log
        options = self.options
        if not silent:
            spinner.start('nuking mongo')
        docker = Docker(log=log)
        containers = docker.get_containers(database='mongo')
        def each(container):
            self.remove(container.name)
        _.for_each(containers, each)
        docker.run('busybox', munchify({
            'daemon': False,
            'rm': True,
            'volume': options.paths.data + ':/data'
        }), 'sh -c "rm -rf /data/* /data/.* 2>/dev/null || true"')
        if not silent:
            spinner.succeed('nuked mongo')

    def restore(self, silent=False, preserve_exit=True):
        log = self.log
        name = self.name
        options = self.options
        daemon = False
        if 'daemon' in options and options.daemon:
            daemon = options.daemon
        if not silent:
            spinner.start('restoring mongo database \'' + name + '\'')
        docker = Docker(log=log)
        container = docker.get_container(name)
        if not container:
            if not silent:
                spinner.warn('\'' + name + '\' does not exist')
            return None
        exited = False
        if container.status == 'exited':
            exited = True
            if not silent and not daemon:
                spinner.stop()
            docker.start(name, {}, daemon=daemon)
        if os.path.exists(options.paths.restore) and os.path.isdir(options.paths.restore):
            copy_tree(
                options.paths.restore,
                options.paths.volumes.restore
            )
        sleep(10)
        if not silent:
            spinner.stop()
        docker.execute(name, munchify({
            'daemon': daemon
        }), '/usr/bin/mongorestore /restore')
        if os.path.exists(options.paths.volumes.restore):
            rm_contents(options.paths.volumes.restore)
        if exited and preserve_exit:
            self.stop()
        if not silent and daemon:
            spinner.succeed('restored mongo database \'' + name + '\'')

    def list(self):
        log = self.log
        docker = Docker(log=log)
        containers = docker.get_containers(database='mongo')
        log.info(_.map_(containers, lambda container: container.name))

    def rename(self, silent=False):
        name = self.name
        if not silent:
            spinner.start('renaming mongo database \'' + name + '\'')
        if not silent:
            spinner.succeed('renamed mongo database \'' + name + '\'')
