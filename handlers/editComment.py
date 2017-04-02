from blogHandler import BlogHandler
from google.appengine.ext import db
from helper import *
from decorators import *

class EditComment(BlogHandler):
    """page to edit a comment"""
    @user_logged_in
    @post_exists
    @comment_exists
    @user_owns_comment
    def get(self, post_id, comment_id, post, comment):
        """display the comment if possible"""
        self.render("editpost.html", subject=comment.subject, content=comment.content, post=post)


    @user_logged_in
    @post_exists
    @comment_exists
    @user_owns_comment
    def post(self, post_id, comment_id, post, comment):
        """save edited comment if possible"""
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
