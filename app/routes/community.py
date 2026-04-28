from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Article, Like, Bookmark, Comment, Follow, Report, Notification
from app.utils import contains_sensitive, filter_sensitive
from app.i18n import t

community_bp = Blueprint('community', __name__)


# ---------- 点赞 ----------

@community_bp.route('/article/<int:article_id>/like', methods=['POST'])
@login_required
def toggle_like(article_id):
    article = Article.query.get_or_404(article_id)
    like = Like.query.filter_by(article_id=article_id, user_id=current_user.id).first()
    if like:
        db.session.delete(like)
        article.like_count = max(0, article.like_count - 1)
        liked = False
    else:
        like = Like(article_id=article_id, user_id=current_user.id)
        db.session.add(like)
        article.like_count += 1
        liked = True
        if article.author_id != current_user.id:
            notif = Notification(
                user_id=article.author_id, type='like',
                content=f'{current_user.username} ❤️ {article.title}',
                link=f'/article/{article_id}'
            )
            db.session.add(notif)
    db.session.commit()
    return jsonify({'liked': liked, 'count': article.like_count})


# ---------- 收藏 ----------

@community_bp.route('/article/<int:article_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(article_id):
    article = Article.query.get_or_404(article_id)
    bm = Bookmark.query.filter_by(article_id=article_id, user_id=current_user.id).first()
    if bm:
        db.session.delete(bm)
        article.bookmark_count = max(0, article.bookmark_count - 1)
        bookmarked = False
    else:
        bm = Bookmark(article_id=article_id, user_id=current_user.id)
        db.session.add(bm)
        article.bookmark_count += 1
        bookmarked = True
    db.session.commit()
    return jsonify({'bookmarked': bookmarked, 'count': article.bookmark_count})


# ---------- 评论 ----------

@community_bp.route('/article/<int:article_id>/comment', methods=['POST'])
@login_required
def add_comment(article_id):
    article = Article.query.get_or_404(article_id)
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    reply_to_user_id = request.form.get('reply_to_user_id', type=int)

    if not content:
        return jsonify({'error': t('comment_empty')}), 400

    sensitive = contains_sensitive(content)
    if sensitive:
        return jsonify({'error': t('error_sensitive_content')}), 400
    content = filter_sensitive(content)

    comment = Comment(
        article_id=article_id, user_id=current_user.id,
        parent_id=parent_id, reply_to_user_id=reply_to_user_id,
        content=content
    )
    db.session.add(comment)
    article.comment_count += 1

    if parent_id:
        parent = Comment.query.get(parent_id)
        if parent and parent.user_id != current_user.id:
            notif = Notification(
                user_id=parent.user_id, type='comment',
                content=f'{current_user.username} 💬',
                link=f'/article/{article_id}'
            )
            db.session.add(notif)
    elif article.author_id != current_user.id:
        notif = Notification(
            user_id=article.author_id, type='comment',
            content=f'{current_user.username} 💬 {article.title}',
            link=f'/article/{article_id}'
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'user': current_user.to_dict(),
        'created_at': comment.created_at.isoformat(),
        'parent_id': comment.parent_id,
    })


@community_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': t('error_no_permission')}), 403
    comment.is_deleted = True
    comment.article.comment_count = max(0, comment.article.comment_count - 1)
    db.session.commit()
    return jsonify({'success': True})


# ---------- 关注 ----------

@community_bp.route('/user/<int:user_id>/follow', methods=['POST'])
@login_required
def toggle_follow(user_id):
    from app.models import User
    target = User.query.get_or_404(user_id)
    if target.id == current_user.id:
        return jsonify({'error': t('follow_self_error')}), 400

    follow = Follow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()
    if follow:
        db.session.delete(follow)
        following = False
    else:
        follow = Follow(follower_id=current_user.id, following_id=user_id)
        db.session.add(follow)
        following = True
        notif = Notification(
            user_id=user_id, type='follow',
            content=f'{current_user.username} 👤',
            link=f'/user/{current_user.id}'
        )
        db.session.add(notif)
    db.session.commit()
    return jsonify({'following': following})


# ---------- 举报 ----------

@community_bp.route('/report', methods=['POST'])
@login_required
def report():
    article_id = request.form.get('article_id', type=int)
    comment_id = request.form.get('comment_id', type=int)
    reason = request.form.get('reason', '').strip()

    if not reason:
        return jsonify({'error': t('article_report_reason')}), 400

    report = Report(
        article_id=article_id, comment_id=comment_id,
        reporter_id=current_user.id, reason=reason
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'message': t('toast_report_submitted')})
