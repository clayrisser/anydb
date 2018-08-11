from cement.core.controller import expose
from cfoundation import Controller

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'manage dotfiles with stow'
        arguments = [
            (['packages'], {
                'action': 'store',
                'help': 'dotfile package names',
                'nargs': '*'
            })
        ]

    @expose()
    def default(self):
        print(self.app.conf)
