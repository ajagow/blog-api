# src/models/UserModel.py
from marshmallow import fields, Schema
import datetime

from sqlalchemy import desc

from . import db, bcrypt
from .PostModel import PostSchema, PostModel
from .InvestmentsModel import InvestorsSchema, InvestmentsModel
from ..shared.Util import get_earnings, is_post_done_hours

class UserModel(db.Model):
  """
  User Model
  """

  # table name
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  email = db.Column(db.String(128), unique=True, nullable=False)
  password = db.Column(db.String(128), nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  thoughts = db.relationship('PostModel', backref='users', lazy=True)
  investments = db.relationship('InvestmentsModel', backref='users', lazy=True)
  net_worth = db.Column(db.Integer, nullable=True)

  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.email = data.get('email')
    self.password = self.__generate_hash(data.get('password'))
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()
    self.net_worth = 100

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      if key == 'password':
        self.password = self.__generate_hash(value)
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_users():
    return UserModel.query.all()

  @staticmethod
  def get_all_users_by_rank():
    return UserModel.query.order_by(desc(UserModel.net_worth)).all()

  @staticmethod
  def get_one_user(id):
    return UserModel.query.get(id)
  
  @staticmethod
  def get_user_by_email(value):
    return UserModel.query.filter_by(email=value).first()

  @staticmethod
  def get_user_networth(id):
    user = UserModel.query.get(id)

    user_ideas = user.thoughts
    user_investments = user.investments

    worth = 100
    for thought in user_ideas:
      initial = thought.initial_worth
      earnings = get_earnings(thought.id, initial)
      if is_post_done_hours(thought, 48):
        worth += earnings

    for investment in user_investments:
      post_id = investment.post_id
      initial_investment = investment.initial_investment

      investment_earnings = get_earnings(post_id, initial_investment)

      if is_post_done_hours(investment, 48):
        worth += investment_earnings

    if worth <= 0:
      return 10

    user.net_worth = worth
    db.session.commit()

    return worth

  @staticmethod
  def get_rankings(id):
    users = UserModel.get_all_users()
    for u in users:
      net_worth = UserModel.get_user_networth(u.id)

      if net_worth <= 0:
        net_worth = 10

      # update each users networth
      u.net_worth = net_worth
      db.session.commit()

    return UserModel.get_all_users_by_rank()




  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)
  
  def __repr(self):
    return '<id {}>'.format(self.id)

class RankingSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  email = fields.Email(required=True)
  net_worth = fields.Int(required=True)

class UserSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  email = fields.Email(required=True)
  password = fields.Str(required=True, load_only=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  thoughts = fields.Nested(PostSchema, many=True)
  investments = fields.Nested(InvestorsSchema, many=True)
  net_worth = fields.Int(required=False)

