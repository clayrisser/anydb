import os, shutil

def rm_contents(path):
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            os.unlink(full_path)
        else:
            shutil.rmtree(full_path)
