from google.appengine.api import memcache
from google.appengine.ext import db

import time
import webapp2
from models import BlogEntry2
from signup import SignupPage
from base import BaseHandler
from login import LoginPage
from welcome import WelcomePage
from ascii import AsciiIndexPage
import urllib2
from xml.dom.minidom import parseString


class IndexPage(BaseHandler):
    def get(self):
        self.render('/templates/index.html')

def get_time_since_last_cache_miss(key):
    last_cache_miss = memcache.get(key)
    now = time.time()

    if last_cache_miss:
        result = now - last_cache_miss
    else:
        result = 0

    return 'Queried %s seconds ago' % int(result)


def get_blog_entries(update = False):
    key = 'blog'
    blog_entries = memcache.get(key)
    if blog_entries is None or update:
        print('CACHE MISS')
        # blog_entries = BlogEntry2.all().order('created')
        blog_entries = db.GqlQuery('SELECT * FROM BlogEntry2 ORDER BY created DESC')
        # Create a list of entries, instead of using the database cursor
        blog_entries = list(blog_entries)
        # Set to memcache
        memcache.set(key, blog_entries)
        memcache.set('time', time.time())

    return blog_entries

def get_blog_entry(key):
    blog_entry = memcache.get(key)
    if not blog_entry:
        print('CACHE MISS')
        blog_entry = BlogEntry2.get_by_id(int(key))
        memcache.set(key, blog_entry)
        memcache.set(key+'_time', time.time())

    return blog_entry


IP_URL = 'http://api.hostip.info/?ip='

def get_coords(ip):
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except URLError:
        return None

    if content:
        dom = parseString(content)
        coords = dom.getElementsByTagName('gml:coordinates')
        if coords and coords[0].childNodes[0].nodeValue:
            lon, lat = coords[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat, lon)

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def gmaps_img(points):
    markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
    return GMAPS_URL + markers

class BlogMainPage(BaseHandler):
    def get(self):
        ip = self.request.remote_addr
        self.write('ip='+repr(get_coords(ip)))
        # blog_entries = db.GqlQuery('SELECT * FROM BlogEntry2 ORDER BY created DESC')
        blog_entries = get_blog_entries()

        # Check what entries have coords
        points = []
        for blog_entry in blog_entries:
            if blog_entry.coords:
                points.append(blog_entry.coords)

        # If we have coords, create an image url
        img_url = None
        if points:
            img_url = gmaps_img(points)

        visits = 0
        visit_cookie_str = self.read_secure_cookie('visits')
        # If there's a cookie 'visits' the user have been here before
        if visit_cookie_str:
            visits = int(visit_cookie_str)
        visits += 1

        self.set_secure_cookie('visits', str(visits))


        query = get_time_since_last_cache_miss('time')

        if self.format == 'html':
            self.render('/templates/blog/index.html',
                        blog_entries=blog_entries,
                        visits=visits,
                        img_url=img_url,
                        query=query
                        )
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

            # Add user coords
            coords = get_coords(self.request.remote_addr)
            if coords:
                b.coords = coords

            # Add the user
            b.creator = self.user

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
        blog_entry = get_blog_entry(blog_entry_id)
        query = get_time_since_last_cache_miss(blog_entry_id+'_time')

        if not blog_entry:
            self.error(404)
            return
        if self.format == 'html':
            self.render('/templates/blog/entry.html',
                        blog_entry_id=blog_entry_id,
                        blog_entry=blog_entry,
                        query=query
                        )
        else:
            self.render_json(blog_entry.as_dict)


class LogoutPage(BaseHandler):
    def get(self):
        for cookie in self.request.cookies:
            self.response.delete_cookie(cookie)
        self.redirect('/blog')


class FlushCache(BaseHandler):
    def get(self):
        # Deletes everything in memcache.
        memcache.flush_all()
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
    (r'/blog/flush', FlushCache),
    (r'/blog/(\d+)/?(?:\.json)?', BlogEntryPage),  # .json is optional
], debug=True)
