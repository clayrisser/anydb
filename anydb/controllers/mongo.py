from cement.core.controller import expose
from cfoundation import Controller
from pydash import _
import os

class Mongo(Controller):
    class Meta:
        label = 'mongo'
        description = 'mongo database'
        stacked_on = 'base'
        stacked_type = 'nested'
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
            (['-d', '--daemon'], {
                'action': 'store_true',
                'help': 'run as daemon',
                'dest': 'daemon',
                'required': False
            }),
            (['--restore-path'], {
                'action': 'store',
                'help': 'restore mongo data',
                'dest': 'restore_path',
                'required': False
            }),
            (['-r', '--restore'], {
                'action': 'store_true',
                'help': 'restore mongo data',
                'dest': 'restore',
                'required': False
            })
        ]

    @expose()
    def default(self):
        conf = self.app.conf
        docker = self.app.docker
        pargs = self.app.pargs
        s = self.app.services
        name = conf.mongo.name
        action = 'start'
        if pargs.name:
            if len(pargs.name) > 1:
                action = pargs.name[0]
                name = pargs.name[len(pargs.name) - 1]
            else:
                name = pargs.name[0]
        port = conf.mongo.port
        if pargs.port:
            port = pargs.port
        port = str(s.util.get_port(int(port))) + ':27017'
        restore = False
        if pargs.restore is not None:
            restore = pargs.restore
        restore_path = None
        if pargs.restore_path:
            restore = True
            restore_path =  os.path.expanduser(pargs.restore_path)
        daemon = False
        if pargs.daemon is not None:
            daemon = pargs.daemon
        exists = False
        def each(value):
            nonlocal exists
            if value.name == name:
                exists = True
        _.for_each(docker.containers.list(all=True), each)
        volumes = [
            os.path.join(conf.data, 'volumes', name, 'data') + ':/data/db',
            os.path.join(conf.data, 'volumes', name, 'restore') + ':/restore'
        ]
        if restore:
            if not exists:
                s.docker.run('mongo', {
                    'name': name,
                    'port': port,
                    'daemon': True,
                    'volume': volumes
                })
            exists = True
            s.docker.execute(name, {}, '/usr/bin/mongorestore /restore')
        if exists:
            return s.docker.start(name, {}, daemon=daemon)
        return s.docker.run('mongo', {
            'name': name,
            'port': port,
            'daemon': daemon,
            'volume': volumes
        })
