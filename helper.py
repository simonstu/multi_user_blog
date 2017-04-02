import re
import hmac
import os
import random
import hashlib
import logging
# logging.info("hello")
from string import letters
from google.appengine.ext import db
import webapp2
import jinja2

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


def blog_key(name='default'):
    """return database key for blogs"""
    return db.Key.from_path('blogs', name)


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