from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Article, User, Category, Tag, Report, SiteConfig, Comment
from app.utils import admin_required, paginate
from app.config import Config
from app.i18n import t

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('auth.login'))


@admin_bp.route('/')
def dashboard():
    stats = {
        'users': User.query.count(),
        'articles': Article.query.count(),
        'published': Article.query.filter_by(status='published').count(),
        'drafts': Article.query.filter_by(status='draft').count(),
        'comments': Comment.query.count(),
        'reports': Report.query.filter_by(status='pending').count(),
    }
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    pending_reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_articles=recent_articles,
                           recent_users=recent_users,
                           pending_reports=pending_reports)


@admin_bp.route('/articles')
def articles():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Article.query
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Article.created_at.desc())
    pagination = paginate(query, page, per_page=20)
    return render_template('admin/articles.html', articles=pagination.items,
                           pagination=pagination, status=status)


@admin_bp.route('/article/<int:article_id>/toggle', methods=['POST'])
def toggle_article(article_id):
    article = Article.query.get_or_404(article_id)
    action = request.form.get('action')
    if action == 'remove':
        article.status = 'removed'
    elif action == 'publish':
        article.status = 'published'
        if not article.published_at:
            article.published_at = datetime.utcnow()
    elif action == 'feature':
        article.is_featured = not article.is_featured
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role', '')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    query = query.order_by(User.created_at.desc())
    pagination = paginate(query, page, per_page=20)
    return render_template('admin/users.html', users=pagination.items,
                           pagination=pagination, role=role)


@admin_bp.route('/user/<int:user_id>/role', methods=['POST'])
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    role = request.form.get('role')
    if role in ('user', 'creator', 'admin'):
        user.role = role
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid role'}), 400


@admin_bp.route('/user/<int:user_id>/toggle_active', methods=['POST'])
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot disable yourself'}), 400
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': user.is_active})


@admin_bp.route('/reports')
def reports():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    query = Report.query
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Report.created_at.desc())
    pagination = paginate(query, page, per_page=20)
    return render_template('admin/reports.html', reports=pagination.items,
                           pagination=pagination, status=status)


@admin_bp.route('/report/<int:report_id>/resolve', methods=['POST'])
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    action = request.form.get('action')
    if action == 'resolve':
        report.status = 'resolved'
        if report.article_id:
            article = Article.query.get(report.article_id)
            if article:
                article.status = 'removed'
    elif action == 'reject':
        report.status = 'rejected'
    report.resolved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        if name:
            cat = Category(name=name, description=description, sort_order=sort_order)
            db.session.add(cat)
            db.session.commit()
            flash(t('toast_save_success'), 'success')
        return redirect(url_for('admin.categories'))
    cats = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/category/<int:cat_id>/delete', methods=['POST'])
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        keys = ['site_name', 'site_logo', 'site_description', 'site_notice',
                'site_footer', 'github_client_id', 'github_client_secret']
        for key in keys:
            value = request.form.get(key, '')
            SiteConfig.set(key, value)
        flash(t('toast_save_success'), 'success')
        return redirect(url_for('admin.settings'))

    config = {}
    for key in ['site_name', 'site_logo', 'site_description', 'site_notice', 'site_footer',
                'github_client_id', 'github_client_secret']:
        config[key] = SiteConfig.get(key)
    return render_template('admin/settings.html', config=config)
