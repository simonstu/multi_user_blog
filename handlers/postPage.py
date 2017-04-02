from blogHandler import BlogHandler
from models import CommentPost
from google.appengine.ext import db
from helper import *
from decorators import *

class PostPage(BlogHandler):
    """page for a single blog post, showing the blog subject, content and all its comments"""
    @post_exists
    def get(self, post_id, post):
        """renders a single blog post"""
        comments = CommentPost.all().order('-created')
        comments.ancestor(post)

        self.render("permalink.html", post=post, user=self.user, comments=comments)