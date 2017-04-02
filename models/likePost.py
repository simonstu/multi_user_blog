from google.appengine.ext import db

class LikePost(db.Model):
    """database model for post likes"""
    post_id = db.IntegerProperty(required=True)
    user_id = db.IntegerProperty(required=True)