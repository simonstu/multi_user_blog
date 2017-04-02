from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from models import LikePost
from decorators import *

class LikePostPage(BlogHandler):
    """page to like a post"""
    @user_logged_in
    @post_exists
    @user_does_not_own_post
    @user_did_not_like_post
    def get(self, post_id, post):
        """add a like to a post"""
        # save like of a post as child of it in the database
        p = LikePost(parent=post, post_id=int(post_id), user_id=self.user.key().id())
        p.put()
        self.redirect(self.request.referer)