from models import User
from base import BaseHandler

class WelcomePage(BaseHandler):
    def render_page(self, username=''):
        self.render('/templates/welcome.html', username=username)

    def get(self):
        uid = self.read_secure_cookie('userId')
        if uid:
            user = User.get_by_id(int(uid))
            if user:
                self.render_page(username=user.username)
            else:
                self.error(404)
                return
