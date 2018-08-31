from cement.core.controller import expose
from cfoundation import Controller
from distutils.dir_util import copy_tree
from munch import munchify
from pydash import _
from time import sleep
import inquirer, os, signal, sys, shutil

class Nuke(Controller):
    class Meta:
        label = 'nuke'
        description = 'nuke all databases'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['name'], {
                'action': 'store',
                'help': 'mongo database name',
                'nargs': '*'
            }),
            (['-f', '--force'], {
                'action': 'store_true',
                'help': 'nuke without prompt',
                'dest': 'force',
                'required': False
            })
        ]

    def nuke(self, database):
        s = self.app.services
        containers = s.docker.get_containers(database=database)
        def for_each(container):
            s.docker.remove_container(container.name)
        _.for_each(containers, for_each)

    @expose()
    def default(self):
        pargs = self.app.pargs
        s = self.app.services
        force = pargs.force
        database = None
        if pargs.name:
            database = pargs.name[0]
        if not force:
            answers = munchify(inquirer.prompt([inquirer.Confirm('nuke', message='nuke databases')]))
            if not answers.nuke:
                print('nuke canceled')
                return
        self.nuke(database)
        print('nuked databases')
