#src/app.py

from flask import Flask

from .config import app_config
from .models import db, bcrypt

# import user_api blueprint
from .views.UserView import user_api as user_blueprint
from .views.PostView import blogpost_api as blogpost_blueprint
from .views.InvestmentsView import investments_api as investments_blueprint
from .views.LIkesView import likes_api as likes_blueprint


def create_app(env_name):
  """
  Create app
  """
  
  # app initiliazation
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])

  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # initializing bcrypt and db
  bcrypt.init_app(app)
  db.init_app(app)

  app.register_blueprint(user_blueprint, url_prefix='/api/v1/users') # add this line
  app.register_blueprint(blogpost_blueprint, url_prefix='/api/v1/posts')
  app.register_blueprint(investments_blueprint, url_prefix='/api/v1/investments')
  app.register_blueprint(likes_blueprint, url_prefix='/api/v1/likes')


  @app.route('/', methods=['GET'])
  def index():
    """
    example endpoint
    """
    return 'Congratulations! Your first endpoint is working'

  return app