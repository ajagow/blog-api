#/src/views/InvestmentsView.py
from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.InvestmentsModel import InvestmentsModel, InvestorsSchema
from ..models.UserModel import UserModel
from ..models.LikesModel import LikesModel
from ..models.PostModel import PostSchema, PostModel
from ..shared.Util import get_earnings, get_total_value

investments_api = Blueprint('investments_api', __name__)
investments_schema = InvestorsSchema()
post_schema = PostSchema()


@investments_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Investment Function
  """
  req_data = request.get_json()
  req_data['investor_id'] = g.user.get('id')

  initial_investment = req_data['initial_investment']
  networth = UserModel.get_user_networth(g.user.get('id'))

  if initial_investment < 0 or initial_investment > networth:
      return custom_response("Invalid investment amount" , 400)

  data, error = investments_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  post = InvestmentsModel(data)
  post.save()
  data = investments_schema.dump(post).data
  return custom_response(data, 201)

# add this function
@investments_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Investments
  """
  posts = InvestmentsModel.get_all_investments()
  data = investments_schema.dump(posts, many=True).data
  return custom_response(data, 200)

@investments_api.route('/<int:post_id>', methods=['GET'])
def get_investment_total_for_post(post_id):
  """
  Get All Investments
  """
  posts = InvestmentsModel.get_investment_total_for_post(post_id)
  data = posts

  return custom_response(data, 200)


@investments_api.route('post/<int:thought_id>', methods=['GET'])
@Auth.auth_required
def get_investors_for_post(thought_id):
    """
    Get investors for a post
    delete me
    """
    post = InvestmentsModel.get_all_investors_for_post(thought_id)
    if not post:
        return custom_response({'error': 'post not found'}, 404)

    data = investments_schema.dump(post, many=True).data

    return custom_response(data, 200)

@investments_api.route('investor/<int:investor_id>', methods=['GET'])
@Auth.auth_required
def get_users_investments(investor_id):
    """
    Get investors for a post
    """
    post = InvestmentsModel.get_all_investors_investments(investor_id)
    if not post:
        return custom_response({'error': 'user not found'}, 404)

    data = investments_schema.dump(post, many=True).data

    return custom_response(data, 200)

@investments_api.route('me/<int:post_id>', methods=['GET'])
@Auth.auth_required
def get_my_investments_for_post(post_id):
    """
    Get investors for a post
    """
    post = InvestmentsModel.get_my_initial_investment_for_post(g.user.get('id'), post_id)
    if not post:
        return custom_response({'error': 'user not found'}, 404)

    # data = investments_schema.dump(post, many=True).data

    data = {"user_total_investment": post}


    return custom_response(data, 200)

@investments_api.route('me', methods=['GET'])
@Auth.auth_required
def get_my_investments():
    """
    Get investors for a post
    """
    post = PostModel.get_investment_posts_for_user(g.user.get('id'), 10)
    if not post:
        return custom_response({'error': 'user not found'}, 404)

    data = post_schema.dump(post, many=True).data

    for d in data:
        post_id = d["id"]
        initial_investment = InvestmentsModel.get_my_initial_investment_for_post(g.user.get('id'), post_id)
        earnings = get_earnings(post_id, initial_investment)
        total_worth = get_total_value(post_id)
        num_investors = InvestmentsModel.get_number_of_investors_for_post(post_id)
        num_likes = LikesModel.get_likes_for_post(post_id)
        num_dislikes = LikesModel.get_dislikes_for_post(post_id)
        d.update({"total_worth": total_worth, "num_investors": num_investors})
        d.update({"earnings": earnings, "my_initial_investment": initial_investment})
        d.update({"num_likes": num_likes, "num_dislikes": num_dislikes})

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
