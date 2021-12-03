from werkzeug.security import check_password_hash

class User:
    def __init__(self, username, email, password):
        self.username=username
        self.email=email
        self.password= password
    
    def is_authenticated(self):
        return True
    
    def is_active():
        return True
    
    def is_anonymous():
        return False
  
    def get_id(self):
        return self.username
  
    def check_password(self,input_password):
        return check_password_hash(self.password,input_password)