"""
文章蓝图
"""

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

from bdwms_blog.emails import send_new_comment_email, send_new_reply_email
from bdwms_blog.extensions import db, cache
from bdwms_blog.models import Post, Category, Comment
from bdwms_blog.utils import redirect_back
from bdwms_blog.forms import CommentForm, AdminCommentForm

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BDWMS_BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
@cache.cached(timeout=5 * 60)
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BDWMS_BLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@cache.cached(timeout=5 * 60)
def show_post(post_id):
    post = Post.query.get_or_404(post_id)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BDWMS_BLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
        page, per_page
    )  # 这篇文章下的，通过评论的，按照评论时间升序
    comments = pagination.items

    if current_user.is_authenticated:  # 如果已经登录用管理员表单
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BDWMS_BLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()  # 否则用普通表单
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body, from_admin=from_admin, post=post, reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        if replied_id:  # 如果存在被回复者，则添加到replied属性中
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)  # 发送回复给被评论者
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # 如果用户已经登录直接显示评论成功
            flash('评论成功', 'success')
        else:
            flash('你的评论将在通过审核后显示', 'info')
            send_new_comment_email(post)  # 发送评论给管理员
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('评论已关闭', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post_id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BDWMS_BLOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)  # cookie过期时间为30天
    return response
