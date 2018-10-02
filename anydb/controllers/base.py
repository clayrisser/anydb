from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version

VERSION_BANNER = """
run any database %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'
        epilog = 'usage: anydb mongo run'
        arguments = [
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]


    def _default(self):
        self.app.args.print_help()

    @ex(
        help='nuke all databases',
    )
    def nuke(self):
        print('nuking all databases')
