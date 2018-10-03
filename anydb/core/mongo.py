from . import Docker

class MongoService():
    def __init__(self, name=None, log=None, options={}):
        self.name = name
        self.log = log
        self.options = options

    def start(self):
        log = self.log
        options = self.options
        docker = Docker(log=log)
        name = self.name
        log.info('starting mongo database \'' + name + '\'')
        container = docker.get_container(name)
        if container:
            log.info('container already exists')
        else:
            docker.run('mongo', {
                'daemon': True,
                'name': name,
                'port': options.port,
                'volume': options.volumes
            })
        if options.reset:
            self.reset()
        if options.restore:
            self.restore()
        if options.rename:
            self.rename()
        return docker.start(name, {}, daemon=options.daemon)

    def restore(self):
        pass

    def reset(self):
        pass

    def rename(self):
        pass
