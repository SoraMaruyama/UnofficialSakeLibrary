from app import db

class Entry(db.Model): 
    __tablename__ = "entries"
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(), nullable=False)
    maker = db.Column(db.String(), nullable=False)

def init():
    db.create_all()