from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


#used by ext.security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    aga_id = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(25))
    current_login_ip = db.Column(db.String(25))
    login_count = db.Column(db.Integer)
    players = relationship("Player")

    def is_server_admin(self):
        return self.has_role('server_admin')

    def is_ratings_admin(self):
        return self.has_role('ratings_admin')

    def __str__(self):
        return "AGA %s, %s" % (self.aga_id, self.email)

class GoServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    url = db.Column(db.String(180))
    token = db.Column(db.Text, unique=True)
    players = db.relationship('Player')

    def __str__(self):
        return self.name

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=user_id)

    token = db.Column(db.Text, unique=True)

    def __str__(self):
        return "Player %s on server %s, user %s" % (self.name, self.server_id, self.user_id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    server_id = db.Column(db.Integer, db.ForeignKey('go_server.id'))
    game_server = db.relationship('GoServer',
                                  foreign_keys=server_id,
                                  backref=db.backref('game_server_id',
                                                     lazy='dynamic'))

    white_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    white = db.relationship('Player',
                            foreign_keys=white_id,
                            backref=db.backref('w_server_account',
                                               lazy='dynamic'))

    black_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    black = db.relationship('Player',
                            foreign_keys=black_id,
                            backref=db.backref('b_server_account',
                                               lazy='dynamic'))

    date_played = db.Column(db.DateTime)
    date_reported = db.Column(db.DateTime)

    result = db.Column(db.String(10))
    rated = db.Column(db.Boolean)
    game_record = db.Column(db.LargeBinary)

    def __str__(self):
        return "Game on %s between %d (b) and %d (w), result %s" % (self.game_server, self.black_id, self.white_id, self.result)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


# Create data for testing
def create_test_data():
    role_user = user_datastore.create_role(
        name='user',
        description='default role'
    )
    role_gs_admin = user_datastore.create_role(
        name='server_admin',
        description='Admin of a Go Server'
    )
    role_aga_admin = user_datastore.create_role(
        name='ratings_admin',
        description='Admin of AGA-Online Ratings'
    )

    u = user_datastore.create_user(email='admin@usgo.org',
                                   password=encrypt_password('usgo'),
                                   id=99)
    user_datastore.add_role_to_user(u, role_aga_admin)

    u = user_datastore.create_user(email='admin@kgs.com',
                                   password=encrypt_password('kgs'),
                                   id=109)
    user_datastore.add_role_to_user(u, role_gs_admin)

    u = user_datastore.create_user(email='foo@foo.com',
                                   password=encrypt_password('foo'),
                                   id=1)
    db.session.add(Player(id=1,name="FooPlayer",server_id=1,user_id=1,token="secret_foo_KGS"))
    db.session.add(Player(id=4,name="FooPlayer",server_id=2,user_id=1,token="secret_foo_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='bar@bar.com',
                                   password=encrypt_password('bar'),
                                   id=2)
    db.session.add(Player(id=2,name="BarPlayer",server_id=1,user_id=2,token="secret_bar_KGS"))
    db.session.add(Player(id=5,name="BarPlayer",server_id=2,user_id=2,token="secret_bar_IGS"))
    user_datastore.add_role_to_user(u, role_user)

    u = user_datastore.create_user(email='baz@baz.com',
                                   password=encrypt_password('baz'),
                                   id=3)
    db.session.add(Player(id=3,name="BazPlayer",server_id=1,user_id=3,token="secret_baz_KGS"))
    db.session.add(Player(id=6,name="BazPlayer",server_id=2,user_id=3,token="secret_baz_IGS"))
    user_datastore.add_role_to_user(u, role_user)


    db.session.add(GoServer(id=1, name='KGS',
                            url='http://gokgs.com',
                            token='secret_kgs'))
    db.session.add(GoServer(id=2, name='IGS',
                            url='http://pandanet.com',
                            token='secret_igs'))

    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5"))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="W+39.5"))
    db.session.add(Game(server_id=2, white_id=3, black_id=2, rated=True, result="W+Resign"))
    db.session.add(Game(server_id=2, white_id=3, black_id=1, rated=True, result="W+Resign"))
    db.session.add(Game(server_id=2, white_id=2, black_id=1, rated=True, result="W+Resign"))
    db.session.add(Game(server_id=1, white_id=1, black_id=2, rated=True, result="B+0.5"))
    db.session.add(Game(server_id=1, white_id=3, black_id=2, rated=True, result="W+39.5"))
    db.session.add(Game(server_id=2, white_id=1, black_id=3, rated=True, result="W+Resign"))

    db.session.commit()
