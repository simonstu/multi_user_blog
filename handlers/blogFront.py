from blogHandler import BlogHandler
from models import Post

class BlogFront(BlogHandler):
    """start page of the blog listing all posts"""
    def get(self):
        """render front page with all posts"""
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts)