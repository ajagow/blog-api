#/src/views/UserView

from flask import request, json, Response, Blueprint, g
from ..models.LikesModel import LikesModel, LikesSchema
from ..models.UserModel import UserModel, UserSchema, RankingSchema
from ..models.PostModel import PostModel, PostSchema
from ..shared.Authentication import Auth

user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()
post_schema = PostSchema()
ranking_schema = RankingSchema()

@user_api.route('/', methods=['POST'])
def create():
  """
  Create User Function
  """
  req_data = request.get_json()
  data, error = user_schema.load(req_data)

  if error:
    return custom_response(error, 400)

  # check if user already exist in the db
  user_in_db = UserModel.get_user_by_email(data.get('email'))
  if user_in_db:
    message = {'error': 'User already exist, please supply another email address'}
    return custom_response(message, 400)

  user = UserModel(data)
  user.save()
  ser_data = user_schema.dump(user).data
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 201)

@user_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get all users
  """
  users = UserModel.get_all_users()
  ser_users = user_schema.dump(users, many=True).data
  return custom_response(ser_users, 200)


@user_api.route('/me', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update me
  """
  req_data = request.get_json()
  data, error = user_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  user = UserModel.get_one_user(g.user.get('id'))
  user.update(data)
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)

@user_api.route('/me', methods=['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a user
  """
  user = UserModel.get_one_user(g.user.get('id'))
  user.delete()
  return custom_response({'message': 'deleted'}, 204)

@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
  """
  Get me
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user).data

  net_worth = UserModel.get_user_networth(g.user.get('id'))

  ser_user.update({"net_worth": net_worth})
  return custom_response(ser_user, 200)


@user_api.route('/rankings', methods=['GET'])
@Auth.auth_required
def get_rankings():
  """
  Get rankings
  """
  users = UserModel.get_rankings(g.user.get('id'))
  data = ranking_schema.dump(users, many=True).data

  ranking = 1
  for d in data:
    d.update({"rank": ranking})
    ranking += 1



  return custom_response(data, 200)

@user_api.route('me/votes', methods=['GET'])
@Auth.auth_required
def get_voting_history():
    """
    Retrieve the voting history of this user
    """
    user_id = g.user.get('id')

    likes = PostModel.get_likes_for_user(user_id, 10)
    dislikes = PostModel.get_dislikes_for_user(user_id, 10)

    if not likes and not dislikes:
        return custom_response({'error': 'no voting history'}, 404)

    like_data = post_schema.dump(likes, many=True).data
    dislike_data = post_schema.dump(dislikes, many=True).data

    for like in like_data:
      like.update({"is_like": True})
      count = add_count(like)
      like.update(count)



    for dislike in dislike_data:
      dislike.update({"is_like": False})
      count = add_count(dislike)
      dislike.update(count)


    data = like_data + dislike_data



    return custom_response(data, 200)

@user_api.route('/login', methods=['POST'])
def login():
  """
  User Login Function
  """
  req_data = request.get_json()

  data, error = user_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  if not data.get('email') or not data.get('password'):
    return custom_response({'error': 'you need email and password to sign in'}, 400)
  user = UserModel.get_user_by_email(data.get('email'))
  if not user:
    return custom_response({'error': 'invalid credentials'}, 400)
  if not user.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials'}, 400)
  ser_data = user_schema.dump(user).data
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 200)



def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

def add_count(data):
  post_id = data.get("id")
  num_dislikes = LikesModel.get_dislikes_for_post(post_id)
  num_likes = LikesModel.get_likes_for_post(post_id)

  return {"num_likes": num_likes, "num_dislikes": num_dislikes}


