from base import BaseHandler

class AsciiIndexPage(BaseHandler):
    def get(self):
        self.render('/templates/ascii/index.html')
