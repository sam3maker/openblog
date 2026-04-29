<div align="center">

# OpenBlog

**Open Source Blog Platform | 开源博客平台**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![TiDB](https://img.shields.io/badge/Database-TiDB-red.svg)](https://tidbcloud.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** | [中文](#中文文档) | [日本語](#日本語ドキュメント) | [한국어](#한국어-문서)

</div>

---

## English

A full-featured open source blog platform with Markdown/rich-text dual editor, community interaction, admin panel, and multi-language support.

### Features

- **Account System** — Register, Login, GitHub OAuth, Password Reset, User Profile
- **Three-tier Roles** — User, Creator, Admin
- **Dual Editor** — Markdown (with live preview) + Rich Text (Quill.js)
- **Content Management** — Categories, Tags, Drafts, Scheduled Publishing, Version History
- **Community** — Likes, Bookmarks, Nested Comments, Follow System, Activity Timeline
- **Admin Panel** — Content Moderation, User Management, Site Configuration, Statistics
- **Multi-language** — 🇨🇳 中文 · 🇺🇸 English · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇫🇷 Français · 🇩🇪 Deutsch · 🇪🇸 Español
- **Dark/Light Theme** — Toggle with auto-persistence
- **Full-text Search** — Search by title, content, summary
- **Image Upload** — With auto-compression and optimization
- **Content Moderation** — Sensitive word filtering, report system

### Quick Start

**1. Clone the repository**
```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
```

**2. Create environment file**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

**3. Install dependencies & run**
```bash
pip install -r requirements.txt
python run.py
```

Visit http://localhost:5000

> The admin account is created automatically on first run. Set the password via the `ADMIN_PASSWORD` environment variable.

### Deploy to Render (Free)

1. Push this repo to your GitHub
2. Sign up at [render.com](https://render.com) (free, no credit card)
3. Click **New** → **Web Service** → Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
5. Add environment variables (see table below)
6. Deploy! Your site will be live at `xxx.onrender.com`

> Note: Free tier sleeps after 15 min of inactivity. It wakes up automatically on the next request.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+ / Flask / SQLAlchemy |
| Frontend | HTML5 / CSS3 / JavaScript / Bootstrap 5 |
| Database | TiDB (MySQL compatible) |
| Editor | Marked.js + Quill.js |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MYSQL_HOST` | Yes | TiDB/MySQL host address |
| `MYSQL_PORT` | Yes | Database port (default: 4000) |
| `MYSQL_USER` | Yes | Database username |
| `MYSQL_PASSWORD` | Yes | Database password |
| `MYSQL_DATABASE` | Yes | Database name (default: openblog) |
| `SECRET_KEY` | Yes | Flask secret key |
| `GITHUB_CLIENT_ID` | No | GitHub OAuth App ID |
| `GITHUB_CLIENT_SECRET` | No | GitHub OAuth App Secret |
| `ADMIN_PASSWORD` | No | Admin account password |

### Project Structure

```
openblog/
├── app/                    # Flask application
│   ├── config.py           # Configuration
│   ├── models.py           # Database models (13 tables)
│   ├── i18n/               # Multi-language translations (7 languages)
│   ├── routes/             # Route blueprints
│   │   ├── auth.py         # Authentication
│   │   ├── blog.py         # Blog CRUD
│   │   ├── community.py    # Social features
│   │   ├── admin.py        # Admin panel
│   │   ├── user.py         # User profiles
│   │   └── api.py          # REST API
│   └── utils.py            # Utilities
├── templates/              # Jinja2 templates
├── static/                 # CSS, JS, uploads
├── requirements.txt
└── run.py
```

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search?q=` | GET | Global search |
| `/api/tags` | GET | Tag list |
| `/api/categories` | GET | Category list |
| `/api/stats` | GET | Site statistics |
| `/api/upload` | POST | Image upload |
| `/api/lang/<code>` | GET | Switch language |

---

<a id="中文文档"></a>

## 中文文档

一个功能完整的开源博客平台，支持 Markdown/富文本双编辑器、社区互动、后台管理、多语言切换。

### 功能特性

- **账号体系** — 注册、登录、GitHub OAuth、密码重置
- **三级权限** — 普通用户 / 创作者 / 管理员
- **双编辑器** — Markdown（实时预览）+ 富文本（Quill.js）
- **内容管理** — 分类、标签、草稿、定时发布、版本历史
- **社区互动** — 点赞、收藏、嵌套评论、关注系统、动态时间线
- **后台管理** — 内容审核、用户管理、站点配置、数据统计
- **多语言** — 🇨🇳 中文 · 🇺🇸 English · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇫🇷 Français · 🇩🇪 Deutsch · 🇪🇸 Español
- **暗黑主题** — 一键切换，自动记忆
- **全文搜索** — 标题、内容、摘要检索
- **图片上传** — 自动压缩优化
- **内容风控** — 敏感词过滤、举报系统

### 快速开始

**1. 克隆仓库**
```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
```

**2. 创建环境文件**
```bash
cp .env.example .env
# 编辑 .env 填入你的数据库凭据
```

**3. 安装依赖并运行**
```bash
pip install -r requirements.txt
python run.py
```

访问 http://localhost:5000

> 管理员账号在首次运行时自动创建。通过 `ADMIN_PASSWORD` 环境变量设置密码。

### 部署到 Render（免费）

1. 推送此仓库到你的 GitHub
2. 在 [render.com](https://render.com) 注册（免费，无需信用卡）
3. 点击 **New** → **Web Service** → 连接你的 GitHub 仓库
4. 配置：
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`gunicorn run:app`
5. 添加环境变量（参考上表）
6. 部署！你的站点将上线于 `xxx.onrender.com`

> 注意：免费套餐在 15 分钟无访问后会休眠，下次请求时自动唤醒。

### 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `MYSQL_HOST` | 是 | TiDB/MySQL 主机地址 |
| `MYSQL_PORT` | 是 | 数据库端口（默认 4000） |
| `MYSQL_USER` | 是 | 数据库用户名 |
| `MYSQL_PASSWORD` | 是 | 数据库密码 |
| `MYSQL_DATABASE` | 是 | 数据库名（默认 openblog） |
| `SECRET_KEY` | 是 | Flask 密钥 |
| `GITHUB_CLIENT_ID` | 否 | GitHub OAuth App ID |
| `GITHUB_CLIENT_SECRET` | 否 | GitHub OAuth App Secret |
| `ADMIN_PASSWORD` | 否 | 管理员账号密码 |

### 数据表

`users` · `articles` · `categories` · `tags` · `tag_article` · `comments` · `likes` · `bookmarks` · `follows` · `article_versions` · `reports` · `site_config` · `notifications`

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+ / Flask / SQLAlchemy |
| 前端 | HTML5 / CSS3 / JavaScript / Bootstrap 5 |
| 数据库 | TiDB（兼容 MySQL 协议） |
| 编辑器 | Marked.js + Quill.js |

---

<a id="日本語ドキュメント"></a>

## 日本語ドキュメント

Markdown・リッチテキストデュアルエディタ、コミュニティ機能、管理画面、多言語対応を備えたオープンソースブログプラットフォーム。

### 機能

- **アカウント** — 登録、ログイン、GitHub OAuth、パスワードリセット
- **3段階権限** — ユーザー / クリエイター / 管理者
- **デュアルエディタ** — Markdown（リアルタイムプレビュー）+ リッチテキスト
- **コンテンツ管理** — カテゴリ、タグ、下書き、予約投稿、バージョン履歴
- **コミュニティ** — いいね、ブックマーク、ネストコメント、フォロー、タイムライン
- **管理画面** — コンテンツ管理、ユーザー管理、サイト設定、統計
- **多言語対応** — 7言語（日本語含む）

### クイックスタート

```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
cp .env.example .env
# .env ファイルを編集してデータベース情報を入力
pip install -r requirements.txt
python run.py
```

http://localhost:5000 にアクセス

### Render にデプロイ（無料）

1. このリポジトリを GitHub にプッシュ
2. [render.com](https://render.com) に登録（無料、クレジットカード不要）
3. **New** → **Web Service** → GitHub リポジトリを接続
4. ビルドコマンド：`pip install -r requirements.txt`、起動コマンド：`gunicorn run:app`
5. 環境変数を設定
6. デプロイ！`xxx.onrender.com` で公開

---

<a id="한국어-문서"></a>

## 한국어 문서

Markdown/리치 텍스트 듀얼 에디터, 커뮤니티, 관리 패널, 다국어 지원 오픈 소스 블로그 플랫폼입니다.

### 기능

- **계정 시스템** — 회원가입, 로그인, GitHub OAuth, 비밀번호 재설정
- **3단계 권한** — 사용자 / 크리에이터 / 관리자
- **듀얼 에디터** — Markdown + 리치 텍스트
- **콘텐츠 관리** — 카테고리, 태그, 임시저장, 예약 발행, 버전 기록
- **커뮤니티** — 좋아요, 북마크, 댓글, 팔로우, 타임라인
- **관리 패널** — 콘텐츠 관리, 사용자 관리, 사이트 설정
- **다국어 지원** — 7개 언어 (한국어 포함)

### 빠른 시작

```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 정보를 입력
pip install -r requirements.txt
python run.py
```

http://localhost:5000 접속

### Render에 배포 (무료)

1. 이 저장소를 GitHub에 푸시
2. [render.com](https://render.com) 가입 (무료, 신용카드 불필요)
3. **New** → **Web Service** → GitHub 저장소 연결
4. 빌드 명령: `pip install -r requirements.txt`, 실행 명령: `gunicorn run:app`
5. 환경변수 설정
6. 배포! `xxx.onrender.com`에서 접속 가능

---

## License

[MIT License](LICENSE)

## Contributing

Issues and Pull Requests are welcome!

---

<div align="center">

**If you like this project, please give it a ⭐!**

</div>
