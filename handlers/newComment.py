from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from models import CommentPost
from decorators import *

class NewComment(BlogHandler):
    """page to add new comment to a post"""
    @user_logged_in
    @post_exists
    def get(self, post_id, post):
        """add a comment to post"""
        self.render("newcomment.html")

    @user_logged_in
    @post_exists
    def post(self, post_id, post):
        """save comment if possible"""
        subject = self.request.get('subject')
        content = self.request.get('content')

        # save comment only if subject and content are not empty, otherwise display error
        if subject and content:
            p = CommentPost(parent=post, subject=subject, content=content,
                            creator=self.user.key().id())
            p.put()
            self.redirect('/blog/%s' % str(post_id))
        else:
            error = "subject and content, please!"
            self.render("newcomment.html", subject=subject, content=content, error=error)
