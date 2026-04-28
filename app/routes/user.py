from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import User, Article, Follow, Bookmark, Notification
from app.utils import save_image, paginate, filter_sensitive
from app.i18n import t

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'articles')

    if tab == 'articles':
        query = Article.query.filter_by(author_id=user_id, status='published')\
            .order_by(Article.published_at.desc())
        pagination = paginate(query, page)
        items = pagination.items
    elif tab == 'bookmarks' and current_user.is_authenticated and current_user.id == user_id:
        query = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.created_at.desc())
        pagination = paginate(query, page)
        items = pagination.items
    else:
        pagination = None
        items = []

    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(user)

    return render_template('user/profile.html', profile_user=user,
                           items=items, pagination=pagination, tab=tab,
                           is_following=is_following)


@user_bp.route('/user/<int:user_id>/followers')
def followers(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'followers')

    if tab == 'followers':
        query = Follow.query.filter_by(following_id=user_id).order_by(Follow.created_at.desc())
    else:
        query = Follow.query.filter_by(follower_id=user_id).order_by(Follow.created_at.desc())

    pagination = paginate(query, page, per_page=30)
    return render_template('user/followers.html', profile_user=user,
                           pagination=pagination, tab=tab)


@user_bp.route('/user/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        signature = request.form.get('signature', '').strip()
        avatar = request.files.get('avatar')

        if username and username != current_user.username:
            if filter_sensitive(username) != username:
                flash(t('error_sensitive_username'), 'error')
            elif User.query.filter(User.username == username, User.id != current_user.id).first():
                flash(t('error_username_exists'), 'error')
            else:
                current_user.username = username

        current_user.bio = bio[:500]
        current_user.signature = signature[:200]

        if avatar and avatar.filename:
            path = save_image(avatar, subdir='avatars', max_size=(200, 200))
            if path:
                current_user.avatar = path

        db.session.commit()
        flash(t('toast_profile_updated'), 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/settings.html')


@user_bp.route('/timeline')
@login_required
def timeline():
    page = request.args.get('page', 1, type=int)
    following_ids = [f.following_id for f in current_user.following.all()]
    if not following_ids:
        return render_template('user/timeline.html', articles=[], pagination=None)

    query = Article.query.filter(
        Article.author_id.in_(following_ids),
        Article.status == 'published'
    ).order_by(Article.published_at.desc())
    pagination = paginate(query, page)
    return render_template('user/timeline.html', articles=pagination.items,
                           pagination=pagination)


@user_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    query = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())
    pagination = paginate(query, page, per_page=20)
    for n in pagination.items:
        n.is_read = True
    db.session.commit()
    return render_template('user/notifications.html', notifications=pagination.items,
                           pagination=pagination)


@user_bp.route('/notifications/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@user_bp.route('/drafts')
@login_required
def drafts():
    page = request.args.get('page', 1, type=int)
    query = Article.query.filter_by(author_id=current_user.id, status='draft')\
        .order_by(Article.updated_at.desc())
    pagination = paginate(query, page)
    return render_template('blog/drafts.html', articles=pagination.items, pagination=pagination)
