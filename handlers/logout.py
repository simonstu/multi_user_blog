from blogHandler import BlogHandler

class Logout(BlogHandler):
    """logout handler"""
    def get(self):
        """logs user out"""
        self.logout()
        self.redirect('/blog')