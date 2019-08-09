# src/models/InvestorsModel.py
from sqlalchemy import func, and_

from . import db
import datetime
from marshmallow import fields, Schema


class InvestmentsModel(db.Model):
  """
  Investment Model
  Keeps track of an Investment a user makes with id, initial investment amount, id of the post they're investing in,
  and id of the user
  """

  __tablename__ = 'investments'

  id = db.Column(db.Integer, primary_key=True)
  initial_investment = db.Column(db.Integer, nullable=False)
  post_id = db.Column(db.Integer, db.ForeignKey('thoughts.id'), nullable=False)
  investor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

  def __init__(self, data):
    self.initial_investment = data.get('initial_investment')
    self.post_id = data.get("post_id")
    self.investor_id = data.get("investor_id")

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
  def get_all_investments():
    """
    Get all investments
    :return: Investment Model list
    """

    return InvestmentsModel.query.all()

  @staticmethod
  def get_number_of_investors_for_post(id):
    """
    Get number of investors for a post.
    :param id: post id
    :return: number of investors for the post
    """
    number_of_investors = InvestmentsModel.query.filter(InvestmentsModel.post_id == id).count()

    if number_of_investors is None:
      return 1
    return number_of_investors + 1

  @staticmethod
  def get_investment_total_for_post(id):
    """
    Get total amount all investors have invested in given post.
    :param id: given post
    :return: investment total for post
    """
    return InvestmentsModel.query.with_entities(func.sum(InvestmentsModel.initial_investment))\
      .filter(InvestmentsModel.post_id == id).scalar()

  @staticmethod
  def get_my_initial_investment_for_post(investor_id, post_id):
    """
    Get how much a user invested in a post
    :param investor_id: user id
    :param post_id: post id
    :return: a user's initial invesment amount for given post
    """
    return InvestmentsModel.query.with_entities(func.sum(InvestmentsModel.initial_investment)).filter(and_(InvestmentsModel.investor_id == investor_id, InvestmentsModel.post_id == post_id)).scalar()

  def __repr__(self):
    return '<id {}>'.format(self.id)


class InvestorsSchema(Schema):
  """
  Investors Schema
  """
  id = fields.Int(dump_only=True)
  initial_investment = fields.Int(required=True)
  investor_id = fields.Int(required=True)
  post_id = fields.Int(required=True)
