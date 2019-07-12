#/src/views/PostView.py
from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.LikesModel import LikesModel, LikesSchema

likes_api = Blueprint('likes_api', __name__)
likes_schema = LikesSchema()

@likes_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Likes Function
  """
  req_data = request.get_json()
  req_data['user_id'] = g.user.get('id')
  data, error = likes_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  post = LikesModel(data)
  post.save()
  data = likes_schema.dump(post).data
  return custom_response(data, 201)

@likes_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Likes
  """
  posts = LikesModel.get_all_likes()
  data = likes_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@likes_api.route('likesForPost/<int:blogpost_id>', methods=['GET'])
def get_likes_for_post(blogpost_id):
    """
    Get likes for a post
    """
    req_data = request.get_json()
    post = LikesModel.get_likes_for_post(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)

    data = json.dumps(post)

    return custom_response(data, 200)

@likes_api.route('dislikesForPost/<int:blogpost_id>', methods=['GET'])
@Auth.auth_required
def get_dislikes_for_post(blogpost_id):
    """
    Get likes for a post
    """
    req_data = request.get_json()
    post = LikesModel.get_dislikes_for_post(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)

    data = json.dumps(post)

    return custom_response(data, 200)


@likes_api.route('/<int:blogpost_id>', methods=['PUT'])
@Auth.auth_required
def update(blogpost_id):
    """
    Update A Blogpost
    """
    req_data = request.get_json()
    post = LikesModel.get_dislikes_for_post(blogpost_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)
    data = likes_schema.dump(post).data

    # might disable this feature
    if data.get('owner_id') != g.user.get('id'):
        return custom_response({'error': 'permission denied'}, 400)

    data, error = likes_schema.load(req_data, partial=True)
    if error:
        return custom_response(error, 400)
    post.update(data)

    data = likes_schema.dump(post).data
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