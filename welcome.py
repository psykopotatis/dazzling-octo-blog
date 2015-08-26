from models import User
from base import BaseHandler

class WelcomePage(BaseHandler):
    def render_page(self, username=''):
        self.render('/templates/welcome.html', username=username)

    def get(self):
        user_id_cookie_str = self.request.cookies.get('userId')
        print(user_id_cookie_str)
        if user_id_cookie_str:
            # Returns the actual user id
            cookie_val = self.check_secure_val(user_id_cookie_str)
            print(cookie_val)
            # If it's OK
            if cookie_val:
                print('OK')
                user = User.get_by_id(int(cookie_val))
                if not user:
                    self.error(404)
                    return
                self.render_page(username=user.username)