from .controllers import Base, Mongo
from .core.exc import AnyDBError
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from munch import munchify
from pydash import _
import os
import yaml

CONFIG = init_defaults('todo')
CONFIG['todo']['foo'] = 'bar'

class AnyDB(App):
    class Meta:
        label = 'anydb'
        config_defaults = CONFIG
        close_on_exit = True
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]
        config_handler = 'yaml'
        config_file_suffix = '.yml'
        log_handler = 'colorlog'
        output_handler = 'jinja2'
        handlers = [
            Base,
            Mongo
        ]

class AnyDBTest(TestApp,AnyDB):
    class Meta:
        label = 'anydb'

def main():
    with AnyDB() as app:
        setattr(app, 'conf', get_conf())
        try:
            app.run()
        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1
            if app.debug is True:
                import traceback
                traceback.print_exc()
        except AnyDBError:
            print('AnyDBError > %s' % e.args[0])
            app.exit_code = 1
            if app.debug is True:
                import traceback
                traceback.print_exc()
        except CaughtSignal as e:
            print('\n%s' % e)
            app.exit_code = 0

def get_conf():
    conf = {}
    with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r') as f:
        conf = yaml.load(f)
    user_conf_path = os.path.join(os.path.expanduser('~'), '.anydb/config.yml')
    if os.path.exists(user_conf_path) and not os.path.isdir(user_conf_path):
        with open(user_conf_path, 'r') as f:
            conf = _.merge(conf, yaml.load(f))
    conf = munchify(conf)
    conf.data = os.path.expanduser(conf.data)
    return conf

if __name__ == '__main__':
    main()
