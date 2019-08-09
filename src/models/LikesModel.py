# src/models/LikesModel.py
from . import db
import datetime
from marshmallow import fields, Schema
from sqlalchemy import and_

class LikesModel(db.Model):
  """
  Likes Model
  """

  __tablename__ = 'likes'

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('thoughts.id'), nullable=False)
  is_like = db.Column(db.Boolean, nullable=False)

  def __init__(self, data):
    self.user_id = data.get('user_id')
    self.post_id = data.get('post_id')
    self.is_like = data.get('is_like')

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
  def get_all_likes():
    """
    Get all likes in the database.
    :return: all likes
    """
    return LikesModel.query.all()

  @staticmethod
  def get_likes_for_post(id):
    """
    Get how many likes there are for a post
    :param id: id of post to get likes for
    :return: total number of likes a post has
    """
    return LikesModel.query.filter(and_(LikesModel.post_id == id, LikesModel.is_like == True)).count()

  @staticmethod
  def get_dislikes_for_post(id):
    """
    Get how many dislikes there are for a post
    :param id: id of post to get dislikes for
    :return: total number of dislikes a post has
    """
    return LikesModel.query.filter(and_(LikesModel.post_id == id, LikesModel.is_like == False)).count()

  @staticmethod
  def get_votes_for_user(id):
    """
    Get votes a user made.
    :param id: user id
    :return: all likes and dislikes of a user
    """
    return LikesModel.query.filter(LikesModel.user_id == id).all()


  def __repr__(self):
    return '<id {}>'.format(self.id)

class LikesSchema(Schema):
  """
  LikesSchema Schema
  """
  id = fields.Int(dump_only=True)
  post_id = fields.Int(required=True)
  user_id = fields.Int(required=True)
  is_like = fields.Boolean(required=True)
