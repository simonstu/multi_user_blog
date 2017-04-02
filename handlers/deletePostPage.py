from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from decorators import *

class DeletePostPage(BlogHandler):
    """page to delete post"""
    @user_logged_in
    @post_exists
    @user_owns_post
    def get(self, post_id, post):
        """delete a post if possible"""
        post.delete()
        self.redirect('/blog')
