"""
登录蓝图
"""
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from bdwms_blog.forms import LoginForm
from bdwms_blog.models import Admin
from bdwms_blog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))

    form = LoginForm()  # 表单类继承的FlaskForm基类默认会从request.form获取表单数据， 所以不需要手动传入
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)  # 登入用户
                flash('欢迎回来', 'info')
                return redirect_back()
            flash('无效的用户名或者密码', 'warning')
        else:
            flash('账户', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功退出', 'info')
    return redirect_back()
