# src/models/PostModel.py
from sqlalchemy.sql.functions import now

from .LikesModel import LikesModel
from .InvestmentsModel import InvestmentsModel
from . import db
import datetime
from marshmallow import fields, Schema
from sqlalchemy import and_, exists, not_, asc, desc


def get_zero_or_value(value):
  if value is None:
    return 0
  return value


class PostModel(db.Model):
  """
  Thought Model
  """

  __tablename__ = 'thoughts'

  id = db.Column(db.Integer, primary_key=True)
  contents = db.Column(db.Text, nullable=False)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  initial_worth = db.Column(db.Integer)
  investment_active = db.Column(db.Boolean)
  market_active = db.Column(db.Boolean)

  def __init__(self, data):
    self.contents = data.get('contents')
    self.owner_id = data.get('owner_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()
    self.initial_worth = data.get("initial_worth")
    self.investment_active = True
    self.market_active = False

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_thought_user(user_id):
    """
    Get all thoughts of a user.
    :param user_id: user id
    :return: all thoughts for user
    """
    return PostModel.query.filter(PostModel.owner_id == user_id).order_by(desc(PostModel.created_at))


  @staticmethod
  def get_market_active_posts_for_user(currentUser, numPosts, lookbackHours, lookbackHoursEnd):
    """
    Get all posts that are market active for a current user.  Posts they haven't seen yet/
    :param currentUser: user id
    :param numPosts: limit number they get per call
    :param lookbackHours: time to start looking
    :param lookbackHoursEnd: time to end
    :return: all posts that make requirements
    """
    look_back_time_start = datetime.timedelta(hours=lookbackHours)
    look_back_start = now() - look_back_time_start

    look_back_time_end = datetime.timedelta(hours=lookbackHoursEnd)
    look_back_end = now() - look_back_time_end

    return PostModel.query.filter(and_(PostModel.created_at < look_back_start, PostModel.created_at > look_back_end, PostModel.owner_id != currentUser))\
    .filter(not_(exists().where(and_(LikesModel.post_id == PostModel.id, LikesModel.user_id == currentUser)))).order_by(asc(PostModel.created_at)).limit(
    numPosts)

  @staticmethod
  def get_investment_posts(currentUser, numPosts, lookbackHours):
    """
    Get investments a user can see.
    :param currentUser: current user id
    :param numPosts: limit how many posts a user can get
    :param lookbackHours: posts made within the past lookbackhours
    :return:
    """
    look_back_time = datetime.timedelta(hours=lookbackHours)
    look_back = now() - look_back_time
    return PostModel.query.filter(and_(PostModel.created_at > look_back, PostModel.owner_id != currentUser))\
      .filter(not_(exists().where(and_(InvestmentsModel.post_id == PostModel.id, InvestmentsModel.investor_id == currentUser)))).order_by(asc(PostModel.created_at)).limit(numPosts)

  @staticmethod
  def get_likes_for_user(currentUser, numPosts):
    """
    Get all posts a user has liked
    :param currentUser: current user id
    :param numPosts: limit number of posts
    :return: all likes for user
    """

    return PostModel.query.filter(exists().where(and_(LikesModel.post_id == PostModel.id, LikesModel.user_id == currentUser, LikesModel.is_like == True))).order_by(asc(PostModel.created_at))\
      .limit(numPosts).all()

  @staticmethod
  def get_dislikes_for_user(currentUser, numPosts):
    """
    Get dislikes for a user.
    :param currentUser: current user id
    :param numPosts: limit number of posts
    :return: all dislikes for user
    """

    return PostModel.query.filter(exists().where(and_(LikesModel.post_id == PostModel.id, LikesModel.user_id == currentUser, LikesModel.is_like == False))).order_by(asc(PostModel.created_at))\
      .limit(numPosts).all()

  @staticmethod
  def get_investment_posts_for_user(currentUser, numPosts):
    """
    Get all investments of a user.
    :param currentUser: current user id
    :param numPosts: limit number of posts
    :return:
    """
    return PostModel.query.filter(exists().where(and_(InvestmentsModel.post_id == PostModel.id, InvestmentsModel.investor_id == currentUser))).order_by(desc(PostModel.created_at))\
      .limit(numPosts).all()

  @staticmethod
  def get_one_thought(id):
    """
    Get one thought by id
    :param id: post id
    :return: the wanted post id
    """
    return PostModel.query.get(id)



  def __repr__(self):
    return '<id {}>'.format(self.id)

class PostSchema(Schema):
  """
  Post Schema
  """
  id = fields.Int(dump_only=True)
  contents = fields.Str(required=True)
  owner_id = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  initial_worth = fields.Integer(required=True)
  investment_active = fields.Boolean()
  market_active = fields.Boolean()
