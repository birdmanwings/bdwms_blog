import os
import click

from flask import Flask, render_template, request
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bdwms_blog.settings import config
from bdwms_blog.extensions import bootstrap, db, csrf, moment, login_manager, ckeditor

from bdwms_blog.models import Admin, Category, Link

from bdwms_blog.blueprints.admin import admin_bp  # 导入蓝图
from bdwms_blog.blueprints.auth import auth_bp
from bdwms_blog.blueprints.blog import blog_bp

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
    return app


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 设置前缀
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_extensions(app):  # 分离拓展的实例化与初始化，因为当实例化放在工厂函数中时，就没有全局的拓展对象
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)


def register_template_context(app):  # 添加模板上下文,这里没写完评论
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        return dict(
            admin=admin, categories=categories,
            links=links)


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
            click.echo('管理员已经存在，更新数据中')
            admin = Admin(username=username, blog_title='bdwmsblog', blog_sub_title='you are good', name='Admin',
                          about='Anything about you')
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('创建默认分类中')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('完成')


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

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400
