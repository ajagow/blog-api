#/src/views/PostView.py
from flask import request, g, Blueprint, json, Response

from src.shared.Util import get_total_value
from ..shared.Authentication import Auth
from ..models.PostModel import PostModel, PostSchema
from ..models.InvestmentsModel import InvestmentsModel

blogpost_api = Blueprint('blogpost_api', __name__)
blogpost_schema = PostSchema()


@blogpost_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Post Function
  """
  req_data = request.get_json()
  req_data['owner_id'] = g.user.get('id')
  data, error = blogpost_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  post = PostModel(data)
  post.save()
  data = blogpost_schema.dump(post).data
  return custom_response(data, 201)

@blogpost_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Blogposts
  """
  posts = PostModel.get_all_blogposts()
  data = blogpost_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@blogpost_api.route('/marketFeedPost/<int:numPosts>/<int:lookbackHours>', methods=['GET'])
@Auth.auth_required
def get_all_market_active(numPosts, lookbackHours):
  """
  Get All Blogposts
  """
  currentUser = g.user.get('id')
  posts = PostModel.get_market_active_posts_for_user(currentUser, numPosts, lookbackHours)
  data = blogpost_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@blogpost_api.route('/value/<int:post_id>', methods=['GET'])
def get_value_of_post(post_id):
  """
  Get All Blogposts
  """
  posts = PostModel.get_value_of_post(post_id)
  data = posts
  return custom_response(data, 200)

@blogpost_api.route('/investments/<int:numPosts>/<int:lookbackHours>', methods=['GET'])
@Auth.auth_required
def get_all_investment_posts(numPosts, lookbackHours):
  """
  Get Investment posts for possible investment
  """
  currentUser = g.user.get('id')
  posts = PostModel.get_investment_posts(currentUser, numPosts, lookbackHours)

  data = blogpost_schema.dump(posts, many=True).data

  for d in data:
      post_id = d.get('id')
      total_worth = get_total_value(post_id)
      num_investors = InvestmentsModel.get_number_of_investors_for_post(post_id)
      d.update({"total_worth": total_worth, "num_investors" : num_investors})

  return custom_response(data, 200)


@blogpost_api.route('/<int:blogpost_id>', methods=['PUT'])
@Auth.auth_required
def update(blogpost_id):
    """
    Update A Blogpost
    """
    req_data = request.get_json()
    post = PostModel.get_one_blogpost(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = blogpost_schema.dump(post).data

    # might disable this feature
    if data.get('owner_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    data, error = blogpost_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)
    post.update(data)

    data = blogpost_schema.dump(post).data
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