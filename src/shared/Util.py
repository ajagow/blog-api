import datetime


from ..models.PostModel import PostModel
from ..models.LikesModel import LikesModel
from ..models.InvestmentsModel import InvestmentsModel
from math import floor

def if_none_then_zero(val):
    """
    If none than return zero
    :param val: value
    :return: val as int
    """
    if val is None:
        return 0
    else:
        return val

def get_total_value(post_id):
    """
    Get total value of post based on initial post amount and all investment amounts
    :param post_id: given post
    :return: total value of post
    """
    post = PostModel.get_one_thought(post_id)
    investment = InvestmentsModel.get_investment_total_for_post(post_id)

    post_initial = if_none_then_zero(post.initial_worth)
    investment = if_none_then_zero(investment)

    return post_initial  + investment


def is_post_done(post):
    """
    Is the post past market active. Past 48 hours.
    :param post: post id
    :return: true if post was created over 48 hours ago
    """
    look_back_time_start = datetime.timedelta(hours=48)
    look_back_start = datetime.datetime.now() - look_back_time_start

    return post.created_at < look_back_start



def get_earnings(post_id, initial_investment):
    """
    Get how much a user earned from a post. Net gain or net lost.
    :param post_id: post id
    :param initial_investment: initial amount a user put in
    :return:
    """
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
        return 0 - initial_investment

