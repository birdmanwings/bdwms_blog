import os

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from flask_login import current_user

from bdwms_blog.blueprints.admin import admin_bp
from bdwms_blog.blueprints.auth import auth_bp
from bdwms_blog.blueprints.blog import blog_bp
from bdwms_blog.extensions import bootstrap, db, login_manager, csrf, ckeditor, moment, mail
from bdwms_blog.models import Admin, Post, Category, Link, Comment
from bdwms_blog.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bdwms_blog')
    app.config.from_object(config[config_name])  # 导入配置

    register_blueprints(app)  # 注册蓝图
    register_extensions(app)  # 注册拓展
    register_template_context(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)
    return app


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 设置前缀


def register_extensions(app):  # 分离拓展的实例化与初始化，因为当实例化放在工厂函数中时，就没有全局的拓展对象
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)


def register_template_context(app):  # 添加模板上下文,这里没写完评论
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:  # 如果当前用户已经登录，就展示未审核的评论数量在base.html
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(
            admin=admin, categories=categories,
            links=links, unread_comments=unread_comments)


def register_shell_context(app):  # 注册shell上下文处理函数
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)


def register_commands(app):
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """创建管理员账户"""
        click.echo('初始化数据库')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('管理员已存在，更新数据中...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('创建管理员账号')
            admin = Admin(
                username=username,
                blog_title='BDWMS',
                blog_sub_title="未来有一个人在等待",
                name='Admin',
                about='一个普通人'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('创建默认分类中')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('完成')

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """初始化数据库"""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)  # 自定义csrf错误响应
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400
