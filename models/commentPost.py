from google.appengine.ext import db
from helper import *

class CommentPost(db.Model):
    """database model for comments to a post"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    creator = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


    def render(self, user, post):
        """how to render a single comment"""
        self._render_text = self.content.replace('\n', '<br>')
        comment = db.get(self.key())
        return render_str("comment.html", c=self, u=user, p=post)