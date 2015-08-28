import webapp2

from models import User, BlogEntry2
from base import BaseHandler
from login import LoginPage
from welcome import WelcomePage


class BlogMainPage(BaseHandler):
    def get(self):
        # blog_entries = db.GqlQuery('SELECT * FROM BlogEntry2 ORDER BY created DESC')
        blog_entries = BlogEntry2.all().order('created')
        # Cookies
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits')
        # If there is a cookie = if this is user have been here before
        if visit_cookie_str:
            cookie_val = self.check_secure_val(visit_cookie_str)
            # If it's secure
            if cookie_val:
                visits = int(cookie_val)

        visits += 1

        new_cookie_val = self.make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

        self.render('/templates/index.html', blog_entries=blog_entries, visits=visits)


class NewPostPage(BaseHandler):
    def render_page(self, subject='', content='', error=''):
        self.render('/templates/newpost.html', subject=subject, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            b = BlogEntry2(subject=subject, content=content)
            # Store this instance in the database
            b.put()
            # Redirect to new url
            self.redirect('/blog/%s' % b.key().id())
        else:
            error_message = 'Error! Need both subject and content.'
            self.render_page(subject, content, error_message)


class BlogEntryPage(BaseHandler):
    def get(self, blog_entry_id):
        blog_entry = BlogEntry2.get_by_id(int(blog_entry_id))
        if not blog_entry:
            self.error(404)
            return
        self.render('/templates/blogentry.html', blog_entry_id=blog_entry_id, blog_entry=blog_entry)


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

            # Store user id in secure cookie
            secure_val = self.make_secure_val(str(new_user.key().id()))

            # 1. Set cookie
            self.response.headers.add_header('Set-Cookie', 'userId=%s;Path=/' % secure_val)
            # 2. Redirect
            self.redirect('/blog/welcome')
        else:
            error = 'Error, you need to fill in all values.'
            self.render_page(username, password, verify, email, error)


class LogoutPage(BaseHandler):
    def get(self):
        for cookie in self.request.cookies:
            self.response.delete_cookie(cookie)
        self.redirect('/blog/signup')



app = webapp2.WSGIApplication([
    (r'/blog', BlogMainPage),
    (r'/blog/signup', SignupPage),
    (r'/blog/welcome', WelcomePage),
    (r'/blog/login', LoginPage),
    (r'/blog/logout', LogoutPage),
    (r'/blog/newpost', NewPostPage),
    (r'/blog/(\d+)', BlogEntryPage),
], debug=True)
