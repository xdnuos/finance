from datetime import datetime
from enum import Enum

from flask_login import UserMixin

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True) 
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True,nullable=False)
    last_name = db.Column(db.String(64), index=True)
    photo_url = db.Column(db.String(128), index=True)
    auth_date = db.Column(db.String(16), index=True,nullable=False)
    def __repr__(self):
        return '<User {}>'.format(self.username) 

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    connect_type = db.Column(db.Integer, db.ForeignKey('connect_type.id'))
    connect_link = db.Column(db.String(128), index=True,nullable=False)
    def __repr__(self):
        return '<Connection {}>'.format(self.connection_id)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    def save(self):
        db.session.add(self)
        db.session.commit()
class ConnectType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True,nullable=False)
    def __repr__(self):
        return '<ConnectType {}>'.format(self.id)

class MonthlyPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64), index=True,nullable=False)
    amount = db.Column(db.Integer,nullable=False)
    datetime = db.Column(db.DateTime, index=True,nullable=False)
    is_income = db.Column(db.Boolean,nullable=False)
    is_paid = db.Column(db.Boolean,nullable=False)
    added = db.Column(db.DateTime, index=True,nullable=False)
    updated = db.Column(db.DateTime, index=True,nullable=False)
    notification = db.Column(db.Boolean,nullable=False)
    def __repr__(self):
        return '<MonthlyPayment {}>'.format(self.name)
class LinkType(Enum):
    GGSHEET = 1
    MESSENGER = 2
class PaymentType(Enum):
    EXPENSE= 1
    INCOME = 2
@login.user_loader
def load_user(id):
    return User.query.get(int(id))