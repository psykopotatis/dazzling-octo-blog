from models import User
from base import BaseHandler


class SignupPage(BaseHandler):
    def render_page(self, username='', password='', verify='', email='', error=''):
        self.render('/templates/signup.html', username=username, password=password, verify=verify, email=email, error=error)

    def get(self):
        self.render_page()

    def post(self):
        print('[POST]', self.request)
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        if username and password and verify:
            password_hash = self.make_password_hash(username, password)
            new_user = User(username=username, password_hash=password_hash, email=email)
            # Store this instance in the database
            new_user.put()

            self.set_secure_cookie('userId', str(new_user.key().id()))

            # 2. Redirect
            self.redirect('/blog/welcome')
        else:
            error = 'Error, you need to fill in all values.'
            self.render_page(username, password, verify, email, error)
