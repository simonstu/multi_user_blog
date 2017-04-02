from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from decorators import *

class EditPost(BlogHandler):
    """page for editing a post"""
    @user_logged_in
    @post_exists
    @user_owns_post
    def get(self, post_id, post):
        """displaying content and subject of a post for editing"""
        self.render("editpost.html", subject=post.subject, content=post.content, post=post)

    @user_logged_in
    @post_exists
    @user_owns_post
    def post(self, post_id, post):
        """save edited post if possible"""
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