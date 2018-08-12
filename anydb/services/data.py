from cfoundation import Service
from munch import munchify, unmunchify
import os
import yaml

class Data(Service):
    def get(self, key=None):
        conf = self.app.conf
        data_path = os.path.join(conf.data, 'data.yml')
        if not os.path.exists(data_path):
            return None
        with open(data_path, 'r') as f:
            data = munchify(yaml.load(f))
            if key:
                return data[key]
            return data

    def set(self, key, value):
        conf = self.app.conf
        data_path = os.path.join(conf.data, 'data.yml')
        data = self.get() or {}
        data[key] = value
        with open(data_path, 'w') as f:
            yaml.dump(unmunchify(data), f, default_flow_style=False)
