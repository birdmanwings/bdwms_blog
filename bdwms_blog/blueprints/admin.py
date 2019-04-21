"""
管理员蓝图
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from bdwms_blog.extensions import db
from bdwms_blog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bdwms_blog.models import Post, Category, Link
from bdwms_blog.utils import redirect_back, allowed_file

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/post/manage')
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title
        current_user.about = form.about.data
        db.session.commit()
        flash('设置更新成功', 'success')
        return redirect(url_for('blog.index'))
