import datetime


from ..models.PostModel import PostModel
from ..models.LikesModel import LikesModel
from ..models.InvestmentsModel import InvestmentsModel
from math import floor

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


def is_post_done(post):
    look_back_time_start = datetime.timedelta(hours=24)
    look_back_start = datetime.datetime.now() - look_back_time_start

    return post.created_at < look_back_start



def get_earnings(post_id, initial_investment):
    post = PostModel.get_one_thought(post_id)
    likes = LikesModel.get_likes_for_post(post_id)
    dislikes = LikesModel.get_dislikes_for_post(post_id)

    likes = if_none_then_zero(likes)
    dislikes = if_none_then_zero(dislikes)

    if is_post_done(post):

        if (likes == 0 and dislikes == 0):
            return 0

        worth = floor(initial_investment * (1 + ((likes - dislikes) / (likes + dislikes))))

        if worth < 0:
            return 0
        else:
            return worth - initial_investment

    else:
        return 0

