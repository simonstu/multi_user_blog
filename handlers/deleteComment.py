from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from decorators import *

class DeleteComment(BlogHandler):
    """page to delete a comment"""
    @user_logged_in
    @post_exists
    @comment_exists
    @user_owns_comment
    def get(self, post_id, comment_id, post, comment):
        """delete comment if possible"""
        comment.delete()
        self.redirect('/blog/%s' % str(post_id))