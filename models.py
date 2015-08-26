from google.appengine.ext import db

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


