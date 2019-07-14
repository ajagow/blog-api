from ..models.PostModel import PostModel
from ..models.LikesModel import LikesModel
from ..models.InvestmentsModel import InvestmentsModel

def if_none_then_zero(val):
    if val is None:
        return 0
    else:
        return val

def get_total_value(post_id):
    post = PostModel.get_one_thought(post_id)
    likes = LikesModel.get_likes_for_post(post_id)
    dislikes = LikesModel.get_dislikes_for_post(post_id)
    investment = InvestmentsModel.get_investment_total_for_post(post_id)

    post_initial = if_none_then_zero(post.initial_worth)
    likes = if_none_then_zero(likes)
    dislikes = if_none_then_zero(dislikes)
    investment = if_none_then_zero(investment)

    return post_initial + likes + dislikes + investment
