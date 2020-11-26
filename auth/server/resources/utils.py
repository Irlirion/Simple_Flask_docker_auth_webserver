from server.resources import db

''' Check if database is available on network '''


def db_available():
    try:
        session = db.create_scoped_session()
        session.execute('SELECT 1')
        return True, "Database OK!"
    except Exception as e:
        return False, str(e)
