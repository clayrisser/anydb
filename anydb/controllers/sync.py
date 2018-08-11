from cement.core.controller import expose
from cfoundation import Controller

class Sync(Controller):
    class Meta:
        label = 'sync'
        description = 'sync dotfiles'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = []

    @expose()
    def default(self):
        print('hi')
