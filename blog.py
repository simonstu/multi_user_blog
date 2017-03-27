"""blog module"""

import os
import re
import random
import hashlib
import hmac
import logging
# logging.info("hello")
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret = '6obdE9sc2hfmqL[EjVJFExG(L{6vm6]*QNzwhaik'


def render_str(template, **params):
    """renders template with given parameters"""
    t = jinja_env.get_template(template)
    return t.render(params)


def make_secure_val(val):
    """return secure val"""
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    """returns val if secure"""
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


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


# user specific classes and methods

def make_salt(length=5):
    """adds random letters"""
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    """makes hash for passwort"""
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    """checks if password is valid"""
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    """returns user key"""
    return db.Key.from_path('users', group)


class User(db.Model):
    """database model for user"""
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        """returns user by id"""
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        """return user by name"""
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        """return new registered user"""
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        """logs user in"""
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


# blog specifc classes and methods

def blog_key(name='default'):
    """return database key for blogs"""
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    """database model for a blog post"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.IntegerProperty(required=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self, user):
        """how to render a single post"""
        self._render_text = self.content.replace('\n', '<br>')
        likes = LikePost.all()
        post = db.get(self.key())
        # show link to like post only if a user is logged in
        if not user:
            return render_str("post.html", p=self, u=user, postLiked=False)
        if post:
            # was this post liked by the user
            likes.ancestor(post)
            likes.filter('user_id =', user.key().id())
            if likes.count() == 1:
                post_liked = True
            else:
                post_liked = False
            return render_str("post.html", p=self, u=user, postLiked=post_liked)
        else:
            return ""


class LikePost(db.Model):
    """database model for post likes"""
    post_id = db.IntegerProperty(required=True)
    user_id = db.IntegerProperty(required=True)


class CommentPost(db.Model):
    """database model for comments to a post"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    creator = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


    def render(self, user, post):
        """how to render a single comment"""
        self._render_text = self.content.replace('\n', '<br>')
        comment = db.get(self.key())
        return render_str("comment.html", c=self, u=user, p=post)


class BlogFront(BlogHandler):
    """start page of the blog listing all posts"""
    def get(self):
        """render front page with all posts"""
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)


class PostPage(BlogHandler):
    """page for a single blog post, showing the blog subject, content and all its comments"""
    def get(self, post_id):
        """renders a single blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        comments = CommentPost.all().order('-created')
        comments.ancestor(post)

        self.render("permalink.html", post=post, user=self.user, comments=comments)


class NewPost(BlogHandler):
    """page to create and save a new post"""
    def get(self):
        """shows page to create new post only if the user is logged in"""
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        """saves new blog post if possible"""
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        # save new post only if subject and content are not empty otherwise display an error
        if subject and content:
            p = Post(parent=blog_key(), subject=subject, content=content,
                     creator=self.user.key().id())
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


class EditPost(BlogHandler):
    """page for editing a post"""
    def get(self, post_id):
        """displaying content and subject of a post for editing"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("editpost.html", subject=post.subject, content=post.content, post=post)

    def post(self, post_id):
        """save edited post if possible"""
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # do not save an edited post if logged in user and creator of the post are different
        if not post.creator == self.user.key().id():
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        # save edited post only if subject and content are not empty, otherwise display error
        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject, content=content, post=post, error=error)


class DeletePostPage(BlogHandler):
    """page to delete post"""
    def get(self, post_id):
        """delete a post if possible"""
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        # do not delete the post if logged in user and creator of the post are different
        if not post.creator == self.user.key().id():
            self.redirect('/blog')

        post.delete()
        self.redirect('/blog')


class LikePostPage(BlogHandler):
    """page to like a post"""
    def get(self, post_id):
        """add a like to a post"""
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        # save like of a post as child of it in the database
        p = LikePost(parent=post, post_id=int(post_id), user_id=self.user.key().id())
        p.put()
        self.redirect(self.request.referer)


class RemoveLikePostPage(BlogHandler):
    """page to remove a like"""
    def get(self, post_id):
        """remove a like of a post"""
        if not self.user:
            self.redirect('/blog')

        likes = LikePost.all()
        # get only the likes of this post and filter them to the id of the current user
        likes.filter('post_id =', int(post_id)).filter('user_id =', self.user.key().id())
        db.delete(likes)
        self.redirect(self.request.referer)


class NewComment(BlogHandler):
    """page to add new comment to a post"""
    def get(self, post_id):
        """add a comment to post"""
        # show page only if user is logged in
        if self.user:
            self.render("newcomment.html")
        else:
            self.redirect("/login")

    def post(self, post_id):
        """save comment if possible"""
        if not self.user:
            self.redirect("/blog")

        subject = self.request.get('subject')
        content = self.request.get('content')

        # save comment only if subject and content are not empty, otherwise display error
        if subject and content:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            p = CommentPost(parent=post, subject=subject, content=content,
                            creator=self.user.key().id())
            p.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            error = "subject and content, please!"
            self.render("newcomment.html", subject=subject, content=content, error=error)


class EditComment(BlogHandler):
    """page to edit a comment"""
    def get(self, post_id, comment_id):
        """display the comment if possible"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        key = db.Key.from_path('CommentPost', int(comment_id), parent=post.key())
        comment = db.get(key)

        if not comment:
            self.error(404)
            return

        self.render("editpost.html", subject=comment.subject, content=comment.content, post=post)


    def post(self, post_id, comment_id):
        """save edited comment if possible"""
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        key = db.Key.from_path('CommentPost', int(comment_id), parent=post.key())
        comment = db.get(key)

        # save edited comment only if logged in user and creator of the comment are not different
        if not comment.creator == self.user.key().id():
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        # save edite comment only if subject and content are not empty, otherwise display error
        if subject and content:
            comment.subject = subject
            comment.content = content
            comment.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject, content=content, post=post, error=error)


class DeleteComment(BlogHandler):
    """page to delete a comment"""
    def get(self, post_id, comment_id):
        """delete comment if possible"""
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        key = db.Key.from_path('CommentPost', int(comment_id), parent=post.key())
        comment = db.get(key)

        if not comment:
            self.error(404)
            return

        # delete comment only if logged in user and creator of the comment are not different
        if not comment.creator == self.user.key().id():
            self.redirect('/blog')

        comment.delete()
        self.redirect('/blog/%s' % str(post_id))

# check for a valid user name
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    """returns username if valid"""
    return username and USER_RE.match(username)

# check for a valid passwort
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    """return password if valid"""
    return password and PASS_RE.match(password)

# check for a valid email
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    """return email if valid"""
    return not email or EMAIL_RE.match(email)


class Signup(BlogHandler):
    """page for signing up"""
    def get(self):
        """renders sign up form"""
        self.render("signup-form.html")

    def post(self):
        """create new use if all entries are valid"""
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        """done"""
        raise NotImplementedError



class Register(Signup):
    """page to register as a user"""
    def done(self):
        """make sure the user doesn't already exist"""
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')


class Login(BlogHandler):
    """loging handler"""
    def get(self):
        """render login form"""
        self.render('login-form.html')

    def post(self):
        """logs user in if valid"""
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):
    """logout handler"""
    def get(self):
        """logs user out"""
        self.logout()
        self.redirect('/blog')


class Welcome(BlogHandler):
    """welcome handler"""
    def get(self):
        """welcomes user if logged in"""
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')


app = webapp2.WSGIApplication([('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletepost/([0-9]+)', DeletePostPage),
                               ('/blog/likepost/([0-9]+)', LikePostPage),
                               ('/blog/removelikepost/([0-9]+)', RemoveLikePostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/newcomment/([0-9]+)', NewComment),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment),
                               ('/blog/signup', Register),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout),
                               ('/blog/welcome', Welcome),
                              ],
                              debug=True)