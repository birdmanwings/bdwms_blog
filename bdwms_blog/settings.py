import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 判断是哪个系统
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEEY', 'dev key')

    # 设定sqlalchemy的配置，不跟踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # 设置ckeditor
    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'

    '''邮箱设定（暂时无）
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('bdwms_blog Admin', MAIL_USERNAME)
    '''

    bdwms_blog_EMAIL = os.getenv('bdwms_blog_EMAIL')  # 邮箱地址
    bdwms_blog_POST_PER_PAGE = 10  # 每页文章数量
    bdwms_blog_MANAGE_POST_PER_PAGE = 15
    bdwms_blog_COMMENT_PER_PAGE = 15  # 评论数目
    # ('theme name', 'display name')
    bdwms_blog_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}
    bdwms_blog_SLOW_QUERY_THRESHOLD = 1

    bdwms_blog_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    bdwms_blog_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


class DevelopmentConfig(BaseConfig):
    '''开发数据库路径'''
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(BaseConfig):
    '''测试配置'''
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(BaseConfig):
    '''生产配置'''
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
