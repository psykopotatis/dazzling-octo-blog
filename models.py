from google.appengine.ext import db


def users_key(group='default'):
    return db.Key.from_path('users', group)

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
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        return User.all().filter('name', name).get()

    @classmethod
    def register(cls, name, password, email):
        pass

    @classmethod
    def login(cls, name, password):
        pass
