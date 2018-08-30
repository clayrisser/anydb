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
        restore = s.util.get_parg('restore')
        action = 'start'
        if pargs.name:
            if pargs.name[0] == 'restore' \
               or pargs.name[0] == 'stop' \
               or pargs.name[0] == 'remove' \
               or pargs.name[0] == 'rm' \
               or pargs.name[0] == 'start' \
               or len(pargs.name) > 1:
                action = pargs.name[0]
                if action == 'restore':
                    if len(pargs.name) < 3:
                        print('expected the restore path')
                        sys.exit(1)
                    restore = pargs.name[len(pargs.name) - 1]
                    name = pargs.name[len(pargs.name) - 2]
                else:
                    name = pargs.name[len(pargs.name) - 1]
            else:
                name = pargs.name[0]
        port = s.util.get_parg('port', conf.mongo.port)
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
        s.docker.stop_container(options.name)
        sys.exit(0)

    def restore(self):
        options = self.options
        s = self.app.services
        if not options.container:
            print('\'' + options.name + '\' does not exist')
            return
        exited = False
        if options.container.status == 'exited':
            exited = True
            s.docker.start(options.name, {}, daemon=True)
        if os.path.exists(options.restore):
            if os.path.isdir(options.restore):
                copy_tree(
                    options.restore,
                    options.paths.volumes.restore
                )
        print('waiting 10 seconds')
        sleep(10)
        s.docker.execute(options.name, {}, '/usr/bin/mongorestore /restore')
        if os.path.exists(options.paths.volumes.restore):
            s.util.rm_contents(options.paths.volumes.restore)
        if exited:
            self.stop()

    def start(self):
        conf = self.app.conf
        options = self.options
        s = self.app.services
        if os.path.exists(options.paths.volumes.restore):
            s.util.rm_contents(options.paths.volumes.restore)
        if options.reset and options.container.status == 'exited':
            if os.path.exists(options.paths.volumes.data):
                s.util.rm_contents(options.paths.volumes.data)
        if not options.container:
            if os.path.exists(options.paths.data):
                shutil.rmtree(options.paths.data)
            s.docker.run('mongo', {
                'name': options.name,
                'port': options.port,
                'daemon': True,
                'volume': options.volumes
            })
        if options.restore:
            self.restore()
        return s.docker.start(options.name, {}, daemon=options.daemon)

    def stop(self):
        options = self.options
        s = self.app.services
        s.docker.stop_container(options.name)

    def remove(self):
        options = self.options
        s = self.app.services
        s.docker.remove_container(options.name)
        if os.path.exists(options.paths.data):
            shutil.rmtree(options.paths.data)

    @expose()
    def default(self):
        options = self.options
        signal.signal(signal.SIGINT, self.handle_sigint)
        if options.action == 'start':
            return self.start()
        elif options.action == 'stop':
            return self.stop()
        elif options.action == 'rm':
            return self.remove()
        elif options.action == 'remove':
            return self.remove()
        elif options.action == 'restore':
            return self.restore()
