from setuptools import setup, find_packages
from anydb.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='anydb',
    version=VERSION,
    description='run any database',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Jam Risser',
    author_email='jam@codejam.ninja',
    url='https://github.com/codejamninja/anydb',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'anydb': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        anydb = anydb.main:main
    """,
)
