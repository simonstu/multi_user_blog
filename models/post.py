from google.appengine.ext import db
from likePost import LikePost
from helper import *

class Post(db.Model):
    """database model for a blog post"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.IntegerProperty(required=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self, user):
        """how to render a single post"""
        self._render_text = self.content.replace('\n', '<br>')
        likes = LikePost.all()
        post = db.get(self.key())
        # show link to like post only if a user is logged in
        if not user:
            return render_str("post.html", p=self, u=user, postLiked=False)
        if post:
            # was this post liked by the user
            likes.ancestor(post)
            likes.filter('user_id =', user.key().id())
            if likes.count() == 1:
                post_liked = True
            else:
                post_liked = False
            return render_str("post.html", p=self, u=user, postLiked=post_liked)
        else:
            return ""