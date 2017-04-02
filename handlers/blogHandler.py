import webapp2
from helper import *
from models import User
from models import Post

class BlogHandler(webapp2.RequestHandler):
    """general handler for the blog"""
    def write(self, *a, **kw):
        """writes response"""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """renders template with added user parameter"""
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        """renders template"""
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """sets secure cookie"""
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """reads secure cookie"""
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """sets cookie for logged in user"""
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """sets cookie if user logs out"""
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """initializes the app and sets user if possible"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
