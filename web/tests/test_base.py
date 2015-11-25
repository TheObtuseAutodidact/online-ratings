from flask.ext.testing import TestCase
from app import app, db

# The test strategy is based on the tutorial found here:
# https://realpython.com/blog/python/python-web-applications-with-flask-part-iii/


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfiguration')
        self.client = app.test_client()
        return app

    def setUp(self):
        db.create_all()
        with app.app_context():
            utils._security.password_hash = 'plaintext'
            create_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
