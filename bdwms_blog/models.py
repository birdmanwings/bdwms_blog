from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bdwms_blog.extensions import db


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码的hash值
    blog_title = db.Column(db.String(60))  # 博客主标题
    blog_sub_title = db.Column(db.String(100))  # 博客副标题
    name = db.Column(db.String(30))
    about = db.Column(db.Text)  # 关于页面

    def set_password(self, password):  # 设置密码，利用password生成hash值
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 验证password是否正确
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', back_populates='category')  # 定义关系属性,back_populates定义反向引用，用于建立双向关系

    def delete(self):
        default_category = Category.query.get(1)  # 获取默认目录
        posts = self.posts[:]  # 获取目录下的所有文章
        for post in posts:  # 更改为默认目录
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 时间戳

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # 设置目录id为外键

    category = db.relationship('Category', back_populates='posts')


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
