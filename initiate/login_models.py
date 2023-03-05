from initiate import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    # columns
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    #init
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password) #sha256 hashing the input salted password
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password) #check if input password matches with salted and hashed password
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #get User with corresponding user_id