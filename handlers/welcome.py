from blogHandler import BlogHandler

class Welcome(BlogHandler):
    """welcome handler"""
    def get(self):
        """welcomes user if logged in"""
        if self.user:
            self.render('welcome.html', username=self.user.name)
        else:
            self.redirect('/signup')