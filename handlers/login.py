from blogHandler import BlogHandler
from models import User

class Login(BlogHandler):
    """loging handler"""
    def get(self):
        """render login form"""
        self.render('login-form.html')

    def post(self):
        """logs user in if valid"""
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)