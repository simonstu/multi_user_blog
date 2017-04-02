from blogHandler import BlogHandler
from models import Post
from helper import *
from google.appengine.ext import db
from decorators import *

class NewPost(BlogHandler):
    """page to create and save a new post"""
    @user_logged_in
    def get(self):
        """shows page to create new post only if the user is logged in"""
        self.render("newpost.html")


    @user_logged_in
    def post(self):
        """saves new blog post if possible"""
        subject = self.request.get('subject')
        content = self.request.get('content')

        # save new post only if subject and content are not empty otherwise display an error
        if subject and content:
            p = Post(parent=blog_key(), subject=subject, content=content,
                     creator=self.user.key().id())
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)