from cement.core.controller import expose
from cfoundation import Controller
from pydash import _

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
            })
        ]

    @expose()
    def default(self):
        conf = self.app.conf
        docker = self.app.docker
        pargs = self.app.pargs
        s = self.app.services
        name = conf.mongo.name
        if pargs.name:
            name = pargs.name[0]
        port = str(conf.mongo.port)
        if pargs.port:
            port = pargs.port
        port = port + ':27017'
        exists = False
        def each(value):
            nonlocal exists
            if value.name == name:
                exists = True
        _.for_each(docker.containers.list(all=True), each)
        s.data.set(name, {
            'port': port,
            'database': 'mongo'
        })
        if exists:
            return s.docker.start(name)
        return s.docker.run('mongo', {
            'name': name,
            'port': port
        })
