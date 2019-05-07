from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_caching import Cache

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
moment = Moment()
ckeditor = CKEditor()
mail = Mail()
migrate = Migrate()
toolbar = DebugToolbarExtension()
cache = Cache()


@login_manager.user_loader
def load_user(user_id):
    """因为session中存储的是用户id，想要获取用户对象需要调用用户加载函数"""
    from bdwms_blog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


"""设置未登录时导向的页面，和返回信息的种类"""
login_manager.login_view = 'auth.login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'
