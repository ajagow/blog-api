#/src/views/InvestmentsView.py
from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.InvestmentsModel import InvestmentsModel, InvestorsSchema

investments_api = Blueprint('investments_api', __name__)
investments_schema = InvestorsSchema()


@investments_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Investment Function
  """
  req_data = request.get_json()
  req_data['investor_id'] = g.user.get('id')
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


@investments_api.route('post/<int:blogpost_id>', methods=['GET'])
@Auth.auth_required
def get_investors_for_post(blogpost_id):
    """
    Get investors for a post
    delete me
    """
    post = InvestmentsModel.get_all_investors_for_post(blogpost_id)
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


def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )