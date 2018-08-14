from cement.core.controller import expose
from cfoundation import Controller
from distutils.dir_util import copy_tree
from munch import munchify
from pydash import _
from time import sleep
import os, signal, sys, shutil

class Mongo(Controller):
    stopping = False

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
            })
        ]

    @property
    def options(self):
        conf = self.app.conf
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
        port = s.util.get_parg('port', conf.mongo.port)
        restore = s.util.get_parg('restore')
        reset = s.util.get_parg('reset')
        daemon = s.util.get_parg('daemon', False)
        port = str(s.util.get_port(int(port))) + ':27017'
        if restore:
            restore = os.path.expanduser(restore)
        container = s.docker.get_container(name)
        data_path = os.path.join(conf.data, 'mongo', name)
        paths = munchify({
            'data': data_path,
            'volumes': {
                'data': os.path.join(data_path, 'volumes/data'),
                'restore': os.path.join(data_path, 'volumes/restore')
            }
        })
        volumes = [
            paths.volumes.data + ':/data/db',
            paths.volumes.restore + ':/restore'
        ]
        return munchify({
            'action': action,
            'container': container,
            'daemon': daemon,
            'name': name,
            'paths': paths,
            'port': port,
            'reset': reset,
            'restore': restore,
            'volumes': volumes
        })

    def handle_sigint(self, sig, frame):
        if not self.stopping:
            print('terminating logs in 5 seconds')
            print('press CTRL-C again to stop database')
            self.stopping = True
            sleep(5)
            return
        docker = self.app.docker
        options = self.options
        s = self.app.services
        s.docker.stop_container(options.name, signal=sig)
        sys.exit(0)

    def start(self, options):
        conf = self.app.conf
        s = self.app.services
        s.util.rm_contents(options.paths.volumes.restore)
        if options.reset and options.container.status == 'exited':
            s.util.rm_contents(options.paths.volumes.data)
        exists = not not options.container
        if options.restore:
            copy_tree(
                options.restore,
                options.paths.volumes.restore
            )
            if not exists:
                s.docker.run('mongo', {
                    'name': options.name,
                    'port': options.port,
                    'daemon': True,
                    'volume': options.volumes
                })
            exists = True
            print('waiting 10 seconds to start')
            sleep(10)
            s.docker.execute(options.name, {}, '/usr/bin/mongorestore /restore')
            s.util.rm_contents(options.paths.volumes.restore)
        if exists:
            signal.signal(signal.SIGINT, self.handle_sigint)
            return s.docker.start(options.name, {}, daemon=options.daemon)
        if os.path.exists(options.paths.data):
            shutil.rmtree(options.paths.data)
        return s.docker.run('mongo', {
            'name': options.name,
            'port': options.port,
            'daemon': options.daemon,
            'volume': options.volumes
        })

    def stop(self, options):
        s = self.app.services
        s.docker.stop_container(options.name, signal.SIGINT)

    def remove(self, options):
        s = self.app.services
        s.docker.remove_container(options.name)
        if os.path.exists(options.paths.data):
            shutil.rmtree(options.paths.data)

    @expose()
    def default(self):
        options = self.options
        if options.action == 'start':
            return self.start(options)
        elif options.action == 'stop':
            return self.stop(options)
        elif options.action == 'rm':
            return self.remove(options)
        elif options.action == 'remove':
            return self.remove(options)
