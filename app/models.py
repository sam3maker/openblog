from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import TEXT
from app import db


# ---------- 用户 ----------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    avatar = db.Column(db.String(500), default='')
    bio = db.Column(db.Text, default='')
    signature = db.Column(db.String(200), default='')
    role = db.Column(db.String(20), default='user')  # user / creator / admin
    github_id = db.Column(db.String(100), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', foreign_keys='Comment.user_id', backref='user', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    following = db.relationship(
        'Follow', foreign_keys='Follow.follower_id',
        backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship(
        'Follow', foreign_keys='Follow.following_id',
        backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_creator(self):
        return self.role in ('creator', 'admin')

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def article_count(self):
        return self.articles.filter_by(status='published').count()

    def is_following(self, user):
        return self.following.filter_by(following_id=user.id).first() is not None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar or '/static/uploads/default_avatar.png',
            'bio': self.bio,
            'signature': self.signature,
            'role': self.role,
            'article_count': self.article_count,
            'follower_count': self.follower_count,
            'following_count': self.following_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ---------- 分类 ----------

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    articles = db.relationship('Article', backref='category', lazy='dynamic')

    @property
    def article_count(self):
        return self.articles.filter_by(status='published').count()


# ---------- 标签 ----------

tag_article = db.Table(
    'tag_article',
    db.Column('article_id', db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# ---------- 文章 ----------

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(TEXT, nullable=False)
    content_html = db.Column(TEXT, default='')
    summary = db.Column(db.String(500), default='')
    cover_image = db.Column(db.String(500), default='')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    editor_type = db.Column(db.String(20), default='markdown')  # markdown / rich_text
    status = db.Column(db.String(20), default='draft', index=True)  # draft / published / scheduled / removed
    is_featured = db.Column(db.Boolean, default=False, index=True)
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    scheduled_at = db.Column(db.DateTime, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    bookmark_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    tags = db.relationship('Tag', secondary=tag_article, backref=db.backref('articles', lazy='dynamic'), lazy='joined')
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    versions = db.relationship('ArticleVersion', backref='article', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'cover_image': self.cover_image,
            'author': self.author.to_dict() if self.author else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'tags': [{'id': t.id, 'name': t.name} for t in self.tags],
            'editor_type': self.editor_type,
            'status': self.status,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'bookmark_count': self.bookmark_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_content:
            data['content'] = self.content
            data['content_html'] = self.content_html
        return data


# ---------- 文章版本 ----------

class ArticleVersion(db.Model):
    __tablename__ = 'article_versions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(TEXT, nullable=False)
    content_html = db.Column(TEXT, default='')
    version_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# ---------- 评论 ----------

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)
    reply_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    reply_to_user = db.relationship('User', foreign_keys=[reply_to_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'user': self.user.to_dict() if self.user else None,
            'parent_id': self.parent_id,
            'reply_to_user': self.reply_to_user.to_dict() if self.reply_to_user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'replies': [r.to_dict() for r in self.replies.filter_by(is_deleted=False).order_by(Comment.created_at)],
        }


# ---------- 点赞 ----------

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('article_id', 'user_id'),)


# ---------- 收藏 ----------

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('article_id', 'user_id'),)


# ---------- 关注 ----------

class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id'),)


# ---------- 举报 ----------

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id', ondelete='SET NULL'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='SET NULL'), nullable=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending / resolved / rejected
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)


# ---------- 站点配置 ----------

class SiteConfig(db.Model):
    __tablename__ = 'site_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    _cache = {}

    @staticmethod
    def get(key, default=''):
        if key in SiteConfig._cache:
            return SiteConfig._cache[key]
        item = SiteConfig.query.filter_by(key=key).first()
        val = item.value if item else default
        SiteConfig._cache[key] = val
        return val

    @staticmethod
    def set(key, value):
        item = SiteConfig.query.filter_by(key=key).first()
        if item:
            item.value = value
        else:
            item = SiteConfig(key=key, value=value)
            db.session.add(item)
        db.session.commit()
        SiteConfig._cache[key] = value


# ---------- 通知 ----------

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # like / comment / follow / system
    content = db.Column(db.Text, default='')
    link = db.Column(db.String(500), default='')
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# ---------- 上传文件（数据库存储）----------

class Upload(db.Model):
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
