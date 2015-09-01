from google.appengine.ext import db
import random
import string
import hashlib


def make_salt():
    return ''.join(random.choice(string.ascii_lowercase) for x in range(5))

def make_password_hash(name, password, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + password + salt).hexdigest()
    return "%s|%s" % (h, salt)

def validate_password(name, password, h):
    salt = h.split('|')[1]
    return h == make_password_hash(name, password, salt)

def users_key(group='default'):
    return db.Key.from_path('users', group)

# ----------------------------------------

class BlogEntry2(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        # Create HTML new lines
        return self.content.replace('\n', '<br>')

class User(db.Model):
    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    email = db.TextProperty(required=False)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return User.all().filter('name', name).get()

    @classmethod
    def register(cls, username, password, email):
        password_hash = make_password_hash(username, password)
        return User(username=username,
                    password_hash=password_hash,
                    email=email)

    @classmethod
    def login(cls, name, password):
        user = cls.by_name(name)
        if user and validate_password(name, password, user.password_hash):
            return user
