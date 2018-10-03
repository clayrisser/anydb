from ..core import Docker
from cement import Controller, ex
from munch import munchify
import os


class Mongo(Controller):
    class Meta:
        label = 'mongo'
        port = 27017
        help = 'mongo database'
        epilog = 'usage: anydb mongo run'
        stacked_on = 'base'
        stacked_type = 'nested'

    @property
    def name(self):
        if not self.app.pargs:
            return ''
        pargs = self.app.pargs
        label = self.Meta.label
        name = 'some' + label
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
        return munchify({
            'data': data_path,
            'volumes': {
                'data': os.path.join(data_path, 'volumes/data'),
                'restore': os.path.join(data_path, 'volumes/restore')
            }
        })

    @property
    def volumes(self):
        paths = self.paths
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
                'nargs': '*'
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
                'dest': 'restore',
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
        pargs = self.app.pargs
        log = self.app.log
        docker = Docker(self.app)
        name = self.name
        log.info('starting mongo database \'' + name + '\'')
        container = docker.get_container(name)
        if container:
            log.info('container already exists')
        else:
            docker.run('mongo', {
                'daemon': True,
                'name': name,
                'port': self.port,
                'volume': self.volumes
            })
        if pargs.reset:
            self.reset()
        if (pargs.restore):
            self.restore()
        return docker.start(name, {}, daemon=pargs.daemon)

    @ex(
        help='stop mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': '*'
            })
        ]
    )
    def stop(self):
        log = self.app.log
        log.info('stopping mongo database \'' + self.name + '\'')

    @ex(
        help='destroy mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': '*'
            })
        ]
    )
    def destroy(self):
        log = self.app.log
        log.info('destroying mongo database \'' + self.name + '\'')

    @ex(
        help='restore mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': '*'
            })
        ]
    )
    def restore(self):
        log = self.app.log
        log.info('restoring mongo database \'' + self.name + '\'')

    @ex(
        help='reset mongo database',
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': '*'
            })
        ]
    )
    def reset(self):
        log = self.app.log
        log.info('resetting mongo database \'' + self.name + '\'')
