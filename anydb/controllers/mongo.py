from ..core import MongoService
from cement import Controller, ex
from halo import Halo
from munch import munchify
from time import sleep
import os, signal

spinner = Halo(spinner='dots')

class Mongo(Controller):
    stopping = False

    class Meta:
        label = 'mongo'
        port = 27017
        help = 'mongo database'
        epilog = 'usage: anydb mongo run'
        stacked_on = 'base'
        stacked_type = 'nested'

    @property
    def name(self):
        if not self.app.pargs or 'name' not in self.app.pargs:
            return None
        pargs = self.app.pargs
        label = self.Meta.label
        name = 'some-' + label
        if len(pargs.name) > 0:
            name = pargs.name[0]
        name = 'anydb_' + label + '_' + name
        return name

    @property
    def port(self):
        if not self.app.pargs:
            return ''
        pargs = self.app.pargs
        port = str(self.Meta.port)
        if pargs.port:
            return pargs.port + ':' + port
        return port + ':' + port

    @property
    def paths(self):
        config = self.app.config
        data_path = os.path.abspath(os.path.expanduser(config.get('anydb', 'data')))
        paths = munchify({
            'data': data_path
        })
        if self.name:
            paths['volumes'] = munchify({
                'data': os.path.join(data_path, self.name, 'volumes/data'),
                'restore': os.path.join(data_path, self.name, 'volumes/restore')
            })
        if self.app.pargs:
            pargs = self.app.pargs
            if 'restore_path' in pargs and pargs.restore_path:
                restore = self.app.pargs.restore_path
                if isinstance(restore, list):
                    restore = restore[0]
                paths['restore'] = os.path.abspath(os.path.expanduser(restore))
        return munchify(paths)

    @property
    def volumes(self):
        paths = self.paths
        if 'volumes' not in paths:
            return []
        return [
            paths.volumes.data + ':/data/db',
            paths.volumes.restore + ':/restore'
        ]

    @ex(
        help='start mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            }),
            (['-p', '--port'], {
                'action': 'store',
                'help': 'mongo database port',
                'dest': 'port',
                'required': False
            }),
            (['--daemon'], {
                'action': 'store_true',
                'help': 'run as daemon',
                'dest': 'daemon',
                'required': False
            }),
            (['-r', '--restore'], {
                'action': 'store',
                'help': 'restore mongo data',
                'dest': 'restore_path',
                'required': False
            }),
            (['--reset'], {
                'action': 'store_true',
                'help': 'reset data',
                'dest': 'reset',
                'required': False
            }),
            (['--rename'], {
                'action': 'store',
                'help': 'rename database',
                'dest': 'rename',
                'required': False
            })
        ]
    )
    def start(self):
        signal.signal(signal.SIGINT, self.handle_sigint)
        pargs = self.app.pargs
        mongo = MongoService(
            name=self.name,
            log=self.app.log,
            options=munchify({
                'daemon': pargs.daemon,
                'port': self.port,
                'rename': pargs.rename,
                'reset': pargs.reset,
                'volumes': self.volumes,
                'paths': self.paths
            })
        )
        mongo.start()

    @ex(
        help='stop mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            })
        ]
    )
    def stop(self):
        mongo = MongoService(
            name=self.name,
            log=self.app.log
        )
        mongo.stop()

    @ex(
        help='remove mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            })
        ]
    )
    def remove(self):
        mongo = MongoService(
            name=self.name,
            log=self.app.log
        )
        mongo.remove()

    @ex(
        help='restore mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            }),
            (['restore_path'], {
                'action': 'store',
                'help': 'restore path',
                'nargs': 1
            })
        ]
    )
    def restore(self):
        pargs = self.app.pargs
        mongo = MongoService(
            name=self.name,
            log=self.app.log,
            options=munchify({
                'paths': self.paths
            })
        )
        mongo.restore()

    @ex(
        help='reset mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            })
        ]
    )
    def reset(self):
        mongo = MongoService(
            name=self.name,
            log=self.app.log,
            options=munchify({
                'paths': self.paths
            })
        )
        mongo.reset()

    @ex(
        help='rename mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': 1
            }),
            (['database_name'], {
                'action': 'store',
                'help': 'mongo database to rename',
                'nargs': 1
            })
        ]
    )
    def rename(self):
        pargs = self.app.pargs
        mongo = MongoService(
            name=self.name,
            log=self.app.log,
            options=munchify({
                'database_name': pargs.database_name[0]
            })
        )
        mongo.rename()

    @ex(
        help='list mongo database'
    )
    def list(self):
        mongo = MongoService(
            log=self.app.log
        )
        mongo.list()

    @ex(
        help='list mongo database'
    )
    def ls(self):
        mongo = MongoService(
            log=self.app.log
        )
        mongo.list()

    @ex(
        help='nuke all mongo databases'
    )
    def nuke(self):
        mongo = MongoService(
            log=self.app.log,
            options=munchify({
                'paths': self.paths
            })
        )
        mongo.nuke()

    def handle_sigint(self, sig, frame):
        log = self.app.log
        config = self.app.config
        timeout = int(config.get('anydb', 'timeout'))
        print()
        if not self.stopping:
            spinner.info('press CTRL-C again to stop database')
            spinner.start('terminating logs in ' + str(timeout) + ' seconds')
            self.stopping = 1
            sleep(timeout)
            return None
        if self.stopping == 1:
            spinner.info('press CTRL-C again to FORCE stop database')
            self.stopping = 2
            self.stop()
        elif self.stopping == 2:
            spinner.warn('forced stopped database')
            exit(1)
