from models import User
from base import BaseHandler

class WelcomePage(BaseHandler):
    def render_page(self, name=''):
        self.render('/templates/welcome.html', name=name)

    def get(self):
        uid = self.read_secure_cookie('userId')
        if uid:
            user = User.get_by_id(int(uid))
            if user:
                self.render_page(name=user.name)
            else:
                self.error(404)
                return
