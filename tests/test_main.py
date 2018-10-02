from anydb.main import AnyDBTest

def test_anydb(tmp):
    with AnyDBTest() as app:
        res = app.run()
        print(res)
        raise Exception

def test_command1(tmp):
    argv = ['command1']
    with AnyDBTest(argv=argv) as app:
        app.run()
