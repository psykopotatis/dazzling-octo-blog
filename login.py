from base import BaseHandler
from models import User

class LoginPage(BaseHandler):
    def render_page(self, username='', password='', error=''):
        self.render('/templates/login.html', username=username, password=password, error=error)

    def get(self):
        self.render_page()

    def post(self):
        print('[POST]', self.request.POST)
        username = self.request.get('username')
        password = self.request.get('password')

        if username and password:
            # Fetch user
            user_query = User.all()
            user_query.filter("username =", username)
            user = user_query.get()
            print('Ok! found: ' + user.username)
            # Extract password hash
            salt = user.password_hash.split('|')[1]
            # Check that password match password_hash
            password_hash = self.make_password_hash(username, password, salt)
            print(password_hash)
            print(user.password_hash)
            if password_hash == user.password_hash:
                print('PASSWORD OK')
                # Store user id in secure cookie
                self.set_secure_cookie('userId', str(user.key().id()))
                # Redirect to welcome page
                self.redirect('/blog/welcome')
            else:
                error = 'Error, username or password wrong.'
                self.render_page(username, password, error)
        else:
            error = 'Error, you need to fill in all values.'
            self.render_page(username, password, error)
