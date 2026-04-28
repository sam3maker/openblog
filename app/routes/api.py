from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Article, Category, Tag, User, SiteConfig
from app.i18n import t

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/search')
def search():
    """全局搜索 API"""
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})
    articles = Article.query.filter(
        Article.status == 'published',
        db.or_(Article.title.contains(q), Article.summary.contains(q))
    ).order_by(Article.published_at.desc()).limit(20).all()
    return jsonify({'results': [a.to_dict() for a in articles]})


@api_bp.route('/tags')
def tags():
    """获取所有标签"""
    q = request.args.get('q', '').strip()
    query = Tag.query
    if q:
        query = query.filter(Tag.name.contains(q))
    tags = query.order_by(Tag.name).limit(50).all()
    return jsonify([{'id': t.id, 'name': t.name} for t in tags])


@api_bp.route('/categories')
def categories():
    """获取所有分类"""
    cats = Category.query.order_by(Category.sort_order).all()
    return jsonify([{'id': c.id, 'name': c.name, 'description': c.description,
                     'article_count': c.article_count} for c in cats])


@api_bp.route('/stats')
def stats():
    """站点统计"""
    return jsonify({
        'users': User.query.count(),
        'articles': Article.query.filter_by(status='published').count(),
        'views': db.session.query(db.func.sum(Article.view_count)).scalar() or 0,
    })


@api_bp.route('/site_config')
def site_config():
    """公开站点配置"""
    return jsonify({
        'site_name': SiteConfig.get('site_name', 'OpenBlog'),
        'site_description': SiteConfig.get('site_description', 'An Open Source Blog Platform'),
        'site_logo': SiteConfig.get('site_logo', ''),
        'site_notice': SiteConfig.get('site_notice', ''),
    })


@api_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """图片上传 API"""
    from app.utils import save_image
    file = request.files.get('file')
    if not file:
        return jsonify({'error': t('error_file_not_selected')}), 400
    path = save_image(file, subdir='images')
    if path:
        return jsonify({'url': path, 'success': True})
    return jsonify({'error': t('error_unsupported_format')}), 400


@api_bp.route('/notifications/read_all', methods=['POST'])
@login_required
def read_all_notifications():
    from app.models import Notification
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/lang/<lang_code>')
def set_language(lang_code):
    """切换语言"""
    from flask import session, redirect, request as req
    from app.i18n import set_language as set_lang, _supported_languages
    if lang_code in _supported_languages:
        set_lang(lang_code)
    return redirect(req.referrer or '/')
