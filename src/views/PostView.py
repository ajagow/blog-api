#/src/views/PostView.py
from flask import request, g, Blueprint, json, Response

from src.shared.Util import get_total_value, get_earnings
from ..shared.Authentication import Auth
from ..models.PostModel import PostModel, PostSchema
from ..models.InvestmentsModel import InvestmentsModel
from ..models.UserModel import UserModel
from ..models.LikesModel import LikesModel


thought_api = Blueprint('thought_api', __name__)
thought_schema = PostSchema()


@thought_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Post Function
  """
  req_data = request.get_json()
  req_data['owner_id'] = g.user.get('id')


  initial_investment = req_data['initial_worth']
  networth = UserModel.get_user_networth(g.user.get('id'))

  if initial_investment < 0 or initial_investment > networth:
      return custom_response("Invalid investment amount" , 400)

  data, error = thought_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  post = PostModel(data)
  post.save()
  data = thought_schema.dump(post).data
  return custom_response(data, 201)

@thought_api.route('/', methods=['GET'])
def get_all():
  """
  Get All thoughts
  """
  posts = PostModel.get_all_thoughts()
  data = thought_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@thought_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_all_thoughts_user():
  """
  Get All thoughts
  """
  currentUser = g.user.get('id')
  posts = PostModel.get_thought_user(currentUser)
  data = thought_schema.dump(posts, many=True).data

  for d in data:
      post_id = d.get('id')

      initial_investment = PostModel.get_one_thought(post_id).initial_worth

      earnings = get_earnings(post_id, initial_investment)
      total_worth = get_total_value(post_id)
      num_investors = InvestmentsModel.get_number_of_investors_for_post(post_id)
      num_likes = LikesModel.get_likes_for_post(post_id)
      num_dislikes = LikesModel.get_dislikes_for_post(post_id)
      d.update({"total_worth": total_worth, "num_investors": num_investors})
      d.update({"earnings": earnings, "my_initial_investment": initial_investment})
      d.update({"num_likes": num_likes, "num_dislikes": num_dislikes})

  return custom_response(data, 200)

@thought_api.route('/marketFeedPost/<int:numPosts>/<int:lookbackHours>/<int:lookbackHoursEnd>', methods=['GET'])
@Auth.auth_required
def get_all_market_active(numPosts, lookbackHours, lookbackHoursEnd):
  """
  Get All thoughts
  """
  currentUser = g.user.get('id')
  posts = PostModel.get_market_active_posts_for_user(currentUser, numPosts, lookbackHours, lookbackHoursEnd)
  data = thought_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@thought_api.route('/value/<int:post_id>', methods=['GET'])
def get_value_of_post(post_id):
  """
  Get All thoughts
  """
  posts = PostModel.get_value_of_post(post_id)
  data = posts
  return custom_response(data, 200)

@thought_api.route('/investments/<int:numPosts>/<int:lookbackHours>', methods=['GET'])
@Auth.auth_required
def get_all_investment_posts(numPosts, lookbackHours):
  """
  Get Investment posts for possible investment
  """
  currentUser = g.user.get('id')
  posts = PostModel.get_investment_posts(currentUser, numPosts, lookbackHours)

  data = thought_schema.dump(posts, many=True).data

  for d in data:
      post_id = d.get('id')
      total_worth = get_total_value(post_id)
      num_investors = InvestmentsModel.get_number_of_investors_for_post(post_id)
      d.update({"total_worth": total_worth, "num_investors" : num_investors})

  return custom_response(data, 200)


@thought_api.route('/<int:thought_id>', methods=['PUT'])
@Auth.auth_required
def update(thought_id):
    """
    Update A thought
    """
    req_data = request.get_json()
    post = PostModel.get_one_thought(thought_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = thought_schema.dump(post).data

    # might disable this feature
    if data.get('owner_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    data, error = thought_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)
    post.update(data)

    data = thought_schema.dump(post).data
    return custom_response(data, 200)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
