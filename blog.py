"""blog module"""

from helper import *

# import database models
from models import User
from models import Post
from models import CommentPost
from models import LikePost

# import handlers
from handlers import BlogHandler
from handlers import BlogFront
from handlers import PostPage
from handlers import NewPost
from handlers import EditPost
from handlers import DeletePostPage
from handlers import LikePostPage
from handlers import RemoveLikePostPage
from handlers import NewComment
from handlers import EditComment
from handlers import DeleteComment
from handlers import Login
from handlers import Logout
from handlers import Welcome
from handlers import Signup
from handlers import Register


app = webapp2.WSGIApplication([('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletepost/([0-9]+)', DeletePostPage),
                               ('/blog/likepost/([0-9]+)', LikePostPage),
                               ('/blog/removelikepost/([0-9]+)', RemoveLikePostPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/newcomment/([0-9]+)', NewComment),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment),
                               ('/blog/signup', Register),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout),
                               ('/blog/welcome', Welcome),
                              ],
                              debug=True)
