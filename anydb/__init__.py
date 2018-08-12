from . import controllers, services
from cfoundation import create_app
from munch import munchify
import docker
import os
import pydash as _
import yaml

client = docker.from_env()

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

conf = get_conf()
if not os.path.exists(conf.data):
    os.makedirs(conf.data)

App = create_app(
    name='anydb',
    controllers=controllers,
    services=services,
    conf=conf,
    docker=client
)
