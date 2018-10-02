from pytest import raises
from anydb.main import AnyDBTest

def test_anydb():
    with AnyDBTest() as app:
        app.run()
        assert app.exit_code == 0


def test_anydb_debug():
    argv = ['--debug']
    with AnyDBTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_command1():
    argv = ['command1']
    with AnyDBTest(argv=argv) as app:
        app.run()
        data,output = app.last_rendered
        assert data['foo'] == 'bar'
        assert output.find('Foo => bar')
    argv = ['command1', '--foo', 'not-bar']
    with AnyDBTest(argv=argv) as app:
        app.run()
        data,output = app.last_rendered
        assert data['foo'] == 'not-bar'
        assert output.find('Foo => not-bar')
