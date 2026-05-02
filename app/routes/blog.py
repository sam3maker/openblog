import time
from xml.sax.saxutils import escape as xml_escape
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response, make_response
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from app import db
from app.models import Article, Category, Tag, ArticleVersion, User
from app.utils import (
    render_markdown, sanitize_html, save_image, paginate,
    contains_sensitive, filter_sensitive, creator_required
)
from app.config import Config
from app.i18n import t

blog_bp = Blueprint('blog', __name__)


# Publish scheduled articles (called on every request)
def _publish_scheduled():
    try:
        Article.query.filter(
            Article.status == 'scheduled',
            Article.scheduled_at <= datetime.now(timezone.utc)
        ).update({'status': 'published', 'published_at': Article.scheduled_at})
        db.session.commit()
    except Exception:
        db.session.rollback()


@blog_bp.before_request
def before_request_hooks():
    # Publish scheduled articles on every page load
    _last = getattr(blog_bp, '_last_publish_check', 0)
    if time.time() - _last > 30:  # at most every 30 seconds
        _publish_scheduled()
        blog_bp._last_publish_check = time.time()


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'latest')
    category_id = request.args.get('category', 0, type=int)
    tag_id = request.args.get('tag', 0, type=int)

    query = Article.query.options(joinedload(Article.author)).filter_by(status='published')
    if category_id:
        query = query.filter_by(category_id=category_id)
    if tag_id:
        query = query.join(Article.tags).filter(Tag.id == tag_id)

    if sort == 'hot':
        query = query.order_by(Article.like_count.desc(), Article.view_count.desc())
    else:
        query = query.order_by(Article.published_at.desc())

    pagination = paginate(query, page)
    articles = pagination.items
    categories = Category.query.order_by(Category.sort_order).all()
    tags = Tag.query.order_by(Tag.created_at.desc()).limit(30).all()

    featured = Article.query.options(joinedload(Article.author)).filter_by(
        status='published', is_featured=True).order_by(
        Article.published_at.desc()).limit(5).all()
    if not featured:
        featured = Article.query.options(joinedload(Article.author)).filter_by(
            status='published').order_by(
            Article.view_count.desc()).limit(5).all()

    return render_template('index.html',
                           articles=articles, pagination=pagination,
                           categories=categories, tags=tags, featured=featured,
                           sort=sort, current_category=category_id, current_tag=tag_id)


@blog_bp.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.options(joinedload(Article.author)).get_or_404(article_id)
    if article.status == 'removed':
        flash(t('admin_status_removed'), 'error')
        return redirect(url_for('blog.index'))
    if article.status == 'draft' and (not current_user.is_authenticated or
                                       current_user.id != article.author_id and not current_user.is_admin):
        flash(t('no_articles'), 'error')
        return redirect(url_for('blog.index'))

    # Atomic view count increment
    db.session.query(Article).filter_by(id=article_id).update(
        {'view_count': Article.view_count + 1})
    db.session.commit()
    db.session.refresh(article)

    is_liked = False
    is_bookmarked = False
    if current_user.is_authenticated:
        from app.models import Like, Bookmark
        is_liked = Like.query.filter_by(article_id=article.id, user_id=current_user.id).first() is not None
        is_bookmarked = Bookmark.query.filter_by(article_id=article.id, user_id=current_user.id).first() is not None

    from app.models import Comment
    comments = Comment.query.options(
        joinedload(Comment.user),
        joinedload(Comment.reply_to_user),
    ).filter_by(article_id=article.id, parent_id=None, is_deleted=False)\
        .order_by(Comment.created_at.desc()).all()

    # Calculate reading time (word-based for CJK, space-based for Latin)
    text = article.content or ''
    cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    words = len(text.split())
    total_words = cjk + words
    reading_time = max(1, total_words // 300)

    return render_template('blog/article.html', article=article, comments=comments,
                           is_liked=is_liked, is_bookmarked=is_bookmarked,
                           reading_time=reading_time, word_count=total_words)


@blog_bp.route('/editor', methods=['GET', 'POST'])
@blog_bp.route('/editor/<int:article_id>', methods=['GET', 'POST'])
@login_required
@creator_required
def editor(article_id=None):
    article = None
    if article_id:
        article = Article.query.get_or_404(article_id)
        if article.author_id != current_user.id and not current_user.is_admin:
            flash(t('error_no_permission'), 'error')
            return redirect(url_for('blog.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        editor_type = request.form.get('editor_type', 'markdown')
        summary = request.form.get('summary', '').strip()
        category_id = request.form.get('category_id', type=int)
        tag_names = request.form.getlist('tags')
        status = request.form.get('status', 'draft')
        scheduled_at_str = request.form.get('scheduled_at', '')
        cover_image = request.files.get('cover_image')

        if not title:
            flash(t('error_title_required'), 'error')
            return redirect(request.url)

        sensitive = contains_sensitive(title + content)
        if sensitive:
            flash(t('error_sensitive_content'), 'error')
            return redirect(request.url)

        if editor_type == 'markdown':
            content_html = sanitize_html(render_markdown(content))
        else:
            content_html = sanitize_html(content)

        cover_path = ''
        if cover_image and cover_image.filename:
            cover_path = save_image(cover_image, subdir='covers', max_size=(800, 450))

        scheduled_at = None
        if status == 'scheduled' and scheduled_at_str:
            try:
                scheduled_at = datetime.strptime(scheduled_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        if article:
            version = ArticleVersion(
                article_id=article.id, title=article.title,
                content=article.content, content_html=article.content_html,
                version_number=article.versions.count() + 1
            )
            db.session.add(version)

            article.title = title
            article.content = content
            article.content_html = content_html
            article.summary = summary[:500]
            article.editor_type = editor_type
            article.category_id = category_id
            article.status = status
            article.scheduled_at = scheduled_at
            if cover_path:
                article.cover_image = cover_path
            if status == 'published' and not article.published_at:
                article.published_at = datetime.now(timezone.utc)
        else:
            article = Article(
                title=title, content=content, content_html=content_html,
                summary=summary[:500], cover_image=cover_path,
                author_id=current_user.id, category_id=category_id,
                editor_type=editor_type, status=status, scheduled_at=scheduled_at,
            )
            if status == 'published':
                article.published_at = datetime.now(timezone.utc)
            db.session.add(article)

        if tag_names:
            article.tags = []
            for name in tag_names:
                name = name.strip()
                if not name:
                    continue
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                article.tags.append(tag)

        db.session.commit()
        flash(t('toast_save_success'), 'success')
        return redirect(url_for('blog.article', article_id=article.id))

    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('blog/editor.html', article=article, categories=categories)


@blog_bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': t('error_no_permission')}), 403
    article.status = 'removed'
    db.session.commit()
    return jsonify({'success': True})


@blog_bp.route('/article/<int:article_id>/versions')
@login_required
def article_versions(article_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': t('error_no_permission')}), 403
    versions = article.versions.order_by(ArticleVersion.version_number.desc()).all()
    return jsonify([{
        'id': v.id, 'title': v.title, 'version_number': v.version_number,
        'created_at': v.created_at.isoformat()
    } for v in versions])


@blog_bp.route('/article/<int:article_id>/version/<int:version_id>')
@login_required
def article_version(article_id, version_id):
    article = Article.query.get_or_404(article_id)
    if article.author_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': t('error_no_permission')}), 403
    from app.models import ArticleVersion
    version = ArticleVersion.query.get_or_404(version_id)
    if version.article_id != article_id:
        return jsonify({'error': 'Version mismatch'}), 400
    return jsonify({
        'id': version.id, 'title': version.title,
        'content': version.content, 'content_html': version.content_html,
        'version_number': version.version_number,
        'created_at': version.created_at.isoformat()
    })


@blog_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    articles = []
    pagination = None
    if q:
        query = Article.query.options(joinedload(Article.author)).filter(
            db.or_(
                Article.title.contains(q),
                Article.summary.contains(q),
                Article.content.contains(q),
            )
        ).filter_by(status='published').order_by(Article.published_at.desc())
        pagination = paginate(query, page)
        articles = pagination.items
    return render_template('blog/search.html', articles=articles, pagination=pagination, q=q)


@blog_bp.route('/category/<int:category_id>')
def category(category_id):
    cat = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    query = Article.query.options(joinedload(Article.author)).filter_by(
        status='published', category_id=category_id
    ).order_by(Article.published_at.desc())
    pagination = paginate(query, page)
    return render_template('blog/category.html', category=cat, articles=pagination.items,
                           pagination=pagination)


@blog_bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': t('error_file_not_selected')}), 400
    path = save_image(file, subdir='images')
    if path:
        return jsonify({'url': path})
    return jsonify({'error': t('error_unsupported_format')}), 400


# ---------- RSS ----------

@blog_bp.route('/feed')
def rss_feed():
    from app.models import SiteConfig
    site_name = SiteConfig.get('site_name', 'OpenBlog')
    site_desc = SiteConfig.get('site_description', 'An Open Source Blog Platform')
    base_url = Config.SITE_URL or request.host_url.rstrip('/')

    articles = Article.query.filter_by(status='published')\
        .order_by(Article.published_at.desc()).limit(20).all()

    items = ''
    for a in articles:
        link = f'{base_url}/article/{a.id}'
        pub_date = a.published_at.strftime('%a, %d %b %Y %H:%M:%S GMT') if a.published_at else ''
        items += f'''<item>
  <title>{xml_escape(a.title)}</title>
  <link>{xml_escape(link)}</link>
  <description>{xml_escape(a.summary[:200])}</description>
  <pubDate>{pub_date}</pubDate>
  <author>{xml_escape(a.author.username if a.author else '')}</author>
</item>'''

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{xml_escape(site_name)}</title>
  <link>{xml_escape(base_url)}</link>
  <description>{xml_escape(site_desc)}</description>
  <language>zh-cn</language>
  {items}
</channel>
</rss>'''
    return Response(xml, mimetype='application/rss+xml')


# ---------- Sitemap & Robots ----------

@blog_bp.route('/sitemap.xml')
def sitemap():
    base_url = Config.SITE_URL or request.host_url.rstrip('/')
    articles = Article.query.filter_by(status='published')\
        .order_by(Article.published_at.desc()).limit(500).all()

    urls = [f'<url><loc>{xml_escape(base_url)}/</loc><changefreq>daily</changefreq></url>']
    for a in articles:
        date = a.published_at.strftime('%Y-%m-%d') if a.published_at else ''
        urls.append(f'<url><loc>{xml_escape(base_url)}/article/{a.id}</loc><lastmod>{date}</lastmod></url>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>'''
    return Response(xml, mimetype='application/xml')


@blog_bp.route('/robots.txt')
def robots():
    base_url = Config.SITE_URL or request.host_url.rstrip('/')
    txt = f'''User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /user/settings
Disallow: /editor

Sitemap: {base_url}/sitemap.xml
'''
    return Response(txt, mimetype='text/plain')
