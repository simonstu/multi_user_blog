from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from models import LikePost
from decorators import *

class RemoveLikePostPage(BlogHandler):
    """page to remove a like"""
    @user_logged_in
    @post_exists
    @user_did_like_post
    def get(self, post_id, post, likes):
        """remove a like of a post"""
        db.delete(likes)
        self.redirect(self.request.referer)