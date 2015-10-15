from google.appengine.api import memcache

import webapp2
from models import BlogEntry2
from signup import SignupPage
from base import BaseHandler
from login import LoginPage
from welcome import WelcomePage
from ascii import AsciiIndexPage


class IndexPage(BaseHandler):
    def get(self):
        self.render('/templates/index.html')

def get_blog_entries(update = False):
    key = 'blog'
    blog_entries = memcache.get(key)
    if blog_entries is None or update:
        print('CACHE MISS')
        blog_entries = BlogEntry2.all().order('created')
        # Create a list of entries, instead of using the database cursor
        blog_entries = list(blog_entries)
        # Set to memcache
        memcache.set(key, blog_entries)

    return blog_entries

class BlogMainPage(BaseHandler):
    def get(self):
        # blog_entries = db.GqlQuery('SELECT * FROM BlogEntry2 ORDER BY created DESC')
        blog_entries = get_blog_entries()

        visits = 0
        visit_cookie_str = self.read_secure_cookie('visits')
        # If there's a cookie 'visits' the user have been here before
        if visit_cookie_str:
            visits = int(visit_cookie_str)
        visits += 1

        self.set_secure_cookie('visits', str(visits))

        if self.format == 'html':
            self.render('/templates/blog/index.html', blog_entries=blog_entries, visits=visits)
        else:
            blog_entries_json = [blog_entry.as_dict() for blog_entry in blog_entries]
            self.render_json(blog_entries_json)


class NewPostPage(BaseHandler):
    def render_page(self, subject='', content='', error=''):
        self.render('/templates/blog/post.html', subject=subject, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            b = BlogEntry2(subject=subject, content=content)
            # Store this instance in the database
            b.put()

            # Rerun query and update cache
            get_blog_entries(True)

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
        if self.format == 'html':
            self.render('/templates/blog/entry.html', blog_entry_id=blog_entry_id, blog_entry=blog_entry)
        else:
            self.render_json(blog_entry.as_dict)


class LogoutPage(BaseHandler):
    def get(self):
        for cookie in self.request.cookies:
            self.response.delete_cookie(cookie)
        self.redirect('/blog')


app = webapp2.WSGIApplication([
    (r'/', IndexPage),
    (r'/ascii/?', AsciiIndexPage),
    (r'/blog/?(?:.json)?', BlogMainPage),  # slash at end is optional, .json is optional
    (r'/blog/signup', SignupPage),
    (r'/blog/welcome', WelcomePage),
    (r'/blog/login', LoginPage),
    (r'/blog/logout', LogoutPage),
    (r'/blog/newpost', NewPostPage),
    (r'/blog/(\d+)/?(?:\.json)?', BlogEntryPage),  # .json is optional
], debug=True)
