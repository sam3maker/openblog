import os
import re
import bleach
import markdown2
from functools import wraps
from flask import jsonify, request
from flask_login import current_user
from PIL import Image
from app.config import Config

# 敏感词列表
_sensitive_words = None


def get_sensitive_words():
    global _sensitive_words
    if _sensitive_words is None:
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sensitive_words.txt')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                _sensitive_words = [w.strip() for w in f.readlines() if w.strip()]
        except FileNotFoundError:
            _sensitive_words = []
    return _sensitive_words


def contains_sensitive(text):
    """检查文本是否包含敏感词，返回匹配到的词列表"""
    words = get_sensitive_words()
    found = []
    for w in words:
        if w in text:
            found.append(w)
    return found


def filter_sensitive(text, replace='*'):
    """替换文本中的敏感词"""
    words = get_sensitive_words()
    for w in words:
        text = text.replace(w, replace * len(w))
    return text


def render_markdown(text):
    """将 Markdown 渲染为 HTML"""
    return markdown2.markdown(
        text,
        extras=['fenced-code-blocks', 'tables', 'code-friendly', 'strike', 'task_list']
    )


def sanitize_html(html):
    """清理 HTML，防止 XSS"""
    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'div',
        'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
        'li', 'ol', 'p', 'pre', 'span', 'strong', 'table', 'tbody',
        'td', 'th', 'thead', 'tr', 'ul', 'del', 'sup', 'sub',
    ]
    allowed_attrs = {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'span': ['class'],
    }
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_image(file, subdir='', max_size=(1200, 1200), quality=85):
    """保存并压缩图片，返回文件路径"""
    if not file or not allowed_file(file.filename):
        return None
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower()
    from datetime import datetime
    new_name = datetime.now().strftime('%Y%m%d%H%M%S') + f'_{os.urandom(4).hex()}.{ext}'
    upload_dir = os.path.join(Config.UPLOAD_FOLDER, subdir)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, new_name)
    img = Image.open(file)
    img.thumbnail(max_size)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.save(filepath, quality=quality, optimize=True)
    return f'/static/uploads/{subdir}/{new_name}'


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '需要管理员权限'}), 403
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated


def creator_required(f):
    """创作者权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_creator:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '需要创作者权限'}), 403
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated


def paginate(query, page=None, per_page=None):
    """分页辅助"""
    page = page or request.args.get('page', 1, type=int)
    per_page = per_page or Config.ARTICLES_PER_PAGE
    return query.paginate(page=page, per_page=per_page, error_out=False)
