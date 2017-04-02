from google.appengine.ext import db
from functools import wraps
from helper import *
from models import LikePost

'''makes sure that a user is logged in'''
def user_logged_in(function):
    @wraps(function)
    def wrapper(self, *args):
        if not self.user:
            self.redirect('/blog')
        else:
            return function(self, *args)
    return wrapper

'''makes sure that a post exists and if passes it along '''
def post_exists(function):
    @wraps(function)
    def wrapper(self, post_id, *args):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if post:
            return function(self, post_id, post=post, *args)
        else:
            self.error(404)
            return
    return wrapper

'''makes sure that a comment exists and if passes it along '''
def comment_exists(function):
    @wraps(function)
    def wrapper(self, post_id, comment_id, post, *args):
        key = db.Key.from_path('CommentPost', int(comment_id), parent=post.key())
        comment = db.get(key)
        if comment:
            return function(self, post_id, comment_id, post, comment=comment, *args)
        else:
            self.error(404)
            return
    return wrapper


'''makes sure that the user own this comment'''
def user_owns_comment(function):
    @wraps(function)
    def wrapper(self, post_id, comment_id, post, comment, *args):
        # delete comment only if logged in user and creator of the comment are not different
        if not comment.creator == self.user.key().id():
            self.redirect('/blog')
        else:
            return function(self, post_id, comment_id, post, comment, *args)
    return wrapper


'''makes sure that the user own this post'''
def user_owns_post(function):
    @wraps(function)
    def wrapper(self, post_id, post, *args):
        # do not delete the post if logged in user and creator of the post are different
        if not post.creator == self.user.key().id():
            self.redirect('/blog')
        else:
            return function(self, post_id, post, *args)
    return wrapper


'''makes sure that the user does not own this post'''
def user_does_not_own_post(function):
    @wraps(function)
    def wrapper(self, post_id, post, *args):
        if post.creator == self.user.key().id():
            self.redirect('/blog')
        else:
            return function(self, post_id, post, *args)
    return wrapper


'''makes sure that the user did not like this post already'''
def user_did_not_like_post(function):
    @wraps(function)
    def wrapper(self, post_id, post, *args):
        likes = LikePost.all()
        # get only the likes of this post and filter them to the id of the current user
        likes.filter('post_id =', int(post_id)).filter('user_id =', self.user.key().id())
        if likes.count() > 0:
            self.redirect('/blog')
        else:
            return function(self, post_id, post, *args)
    return wrapper


'''makes sure that the user already liked this post'''
def user_did_like_post(function):
    @wraps(function)
    def wrapper(self, post_id, post, *args):
        likes = LikePost.all()
        # get only the likes of this post and filter them to the id of the current user
        likes.filter('post_id =', int(post_id)).filter('user_id =', self.user.key().id())
        if likes.count() == 1:
            return function(self, post_id, post, likes=likes, *args)
        else:
            self.redirect('/blog')
    return wrapper