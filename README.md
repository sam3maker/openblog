---
title: OpenBlog
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

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

**3. Download SSL certificate**

This project uses TiDB Cloud, which requires an SSL certificate to connect. Register a free account at [TiDB Cloud](https://tidbcloud.com), create a cluster, and download the `isrgrootx1.pem` certificate from the cluster connection page. Place it in the project root directory.

**4. Install dependencies & run**
```bash
pip install -r requirements.txt
python run.py
```

Visit http://localhost:5000

> The admin account is created automatically on first run. Set the password via the `ADMIN_PASSWORD` environment variable.

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
| `MYSQL_SSL_CA_CONTENT` | No | SSL cert file content (for deployment without pem file) |

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

**3. 下载 SSL 证书**

本项目使用 TiDB Cloud 数据库，连接需要 SSL 证书。请在 [TiDB Cloud](https://tidbcloud.com) 注册免费账号，创建集群后，在集群连接页面下载 `isrgrootx1.pem` 证书文件，放到项目根目录。

**4. 安装依赖并运行**
```bash
pip install -r requirements.txt
python run.py
```

访问 http://localhost:5000

> 管理员账号在首次运行时自动创建。通过 `ADMIN_PASSWORD` 环境变量设置密码。

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
| `MYSQL_SSL_CA_CONTENT` | 否 | SSL 证书文件内容（用于无 pem 文件的部署环境） |

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

- **アカウント** — 登録、ログイン、GitHub OAuth、パスワードリセット、プロフィール
- **3段階権限** — ユーザー / クリエイター / 管理者
- **デュアルエディタ** — Markdown（リアルタイムプレビュー）+ リッチテキスト（Quill.js）
- **コンテンツ管理** — カテゴリ、タグ、下書き、予約投稿、バージョン履歴
- **コミュニティ** — いいね、ブックマーク、ネストコメント、フォロー、タイムライン
- **管理画面** — コンテンツ審査、ユーザー管理、サイト設定、統計
- **多言語対応** — 🇨🇳 中文 · 🇺🇸 English · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇫🇷 Français · 🇩🇪 Deutsch · 🇪🇸 Español
- **ダーク/ライトテーマ** — ワンクリック切替、自動記憶
- **全文検索** — タイトル、本文、概要から検索
- **画像アップロード** — 自動圧縮・最適化付き
- **コンテンツ審査** — 機微語句フィルタリング、通報システム

### クイックスタート

```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
cp .env.example .env
# .env ファイルを編集してデータベース情報を入力
```

[TiDB Cloud](https://tidbcloud.com) で無料アカウントを登録し、クラスタを作成後、接続ページから `isrgrootx1.pem` 証明書をダウンロードしてプロジェクトルートに配置してください。

```bash
pip install -r requirements.txt
python run.py
```

http://localhost:5000 にアクセス

> 管理者アカウントは初回起動時に自動作成されます。`ADMIN_PASSWORD` 環境変数でパスワードを設定してください。

### 環境変数

| 変数 | 必須 | 説明 |
|------|------|------|
| `MYSQL_HOST` | はい | TiDB/MySQL ホストアドレス |
| `MYSQL_PORT` | はい | データベースポート（デフォルト: 4000） |
| `MYSQL_USER` | はい | データベースユーザー名 |
| `MYSQL_PASSWORD` | はい | データベースパスワード |
| `MYSQL_DATABASE` | はい | データベース名（デフォルト: openblog） |
| `SECRET_KEY` | はい | Flask シークレットキー |
| `GITHUB_CLIENT_ID` | いいえ | GitHub OAuth App ID |
| `GITHUB_CLIENT_SECRET` | いいえ | GitHub OAuth App シークレット |
| `ADMIN_PASSWORD` | いいえ | 管理者アカウントのパスワード |
| `MYSQL_SSL_CA_CONTENT` | いいえ | SSL証明書ファイルの内容（pemファイルなしのデプロイ用） |

### テクノロジースタック

| レイヤー | 技術 |
|----------|------|
| バックエンド | Python 3.10+ / Flask / SQLAlchemy |
| フロントエンド | HTML5 / CSS3 / JavaScript / Bootstrap 5 |
| データベース | TiDB（MySQL 互換） |
| エディタ | Marked.js + Quill.js |

---

<a id="한국어-문서"></a>

## 한국어 문서

Markdown/리치 텍스트 듀얼 에디터, 커뮤니티, 관리 패널, 다국어 지원 오픈 소스 블로그 플랫폼입니다.

### 기능

- **계정 시스템** — 회원가입, 로그인, GitHub OAuth, 비밀번호 재설정, 프로필
- **3단계 권한** — 사용자 / 크리에이터 / 관리자
- **듀얼 에디터** — Markdown (실시간 미리보기) + 리치 텍스트 (Quill.js)
- **콘텐츠 관리** — 카테고리, 태그, 임시저장, 예약 발행, 버전 기록
- **커뮤니티** — 좋아요, 북마크, 중첩 댓글, 팔로우, 타임라인
- **관리 패널** — 콘텐츠 검수, 사용자 관리, 사이트 설정, 통계
- **다국어 지원** — 🇨🇳 中文 · 🇺🇸 English · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇫🇷 Français · 🇩🇪 Deutsch · 🇪🇸 Español
- **다크/라이트 테마** — 원클릭 전환, 자동 저장
- **전문 검색** — 제목, 본문, 요약 검색
- **이미지 업로드** — 자동 압축 및 최적화
- **콘텐츠 검수** — 민감어 필터링, 신고 시스템

### 빠른 시작

```bash
git clone https://github.com/sam3maker/openblog.git
cd openblog
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 정보를 입력
```

[TiDB Cloud](https://tidbcloud.com) 에서 무료 계정을 등록하고 클러스터를 생성한 후, 연결 페이지에서 `isrgrootx1.pem` 인증서를 다운로드하여 프로젝트 루트에 배치하세요.

```bash
pip install -r requirements.txt
python run.py
```

http://localhost:5000 접속

> 관리자 계정은 첫 실행 시 자동 생성됩니다. `ADMIN_PASSWORD` 환경 변수로 비밀번호를 설정하세요.

### 환경 변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `MYSQL_HOST` | 예 | TiDB/MySQL 호스트 주소 |
| `MYSQL_PORT` | 예 | 데이터베이스 포트 (기본값: 4000) |
| `MYSQL_USER` | 예 | 데이터베이스 사용자명 |
| `MYSQL_PASSWORD` | 예 | 데이터베이스 비밀번호 |
| `MYSQL_DATABASE` | 예 | 데이터베이스명 (기본값: openblog) |
| `SECRET_KEY` | 예 | Flask 시크릿 키 |
| `GITHUB_CLIENT_ID` | 아니오 | GitHub OAuth App ID |
| `GITHUB_CLIENT_SECRET` | 아니오 | GitHub OAuth App 시크릿 |
| `ADMIN_PASSWORD` | 아니오 | 관리자 계정 비밀번호 |
| `MYSQL_SSL_CA_CONTENT` | 아니오 | SSL 인증서 파일 내용 (pem 파일 없는 배포용) |

### 기술 스택

| 계층 | 기술 |
|------|------|
| 백엔드 | Python 3.10+ / Flask / SQLAlchemy |
| 프론트엔드 | HTML5 / CSS3 / JavaScript / Bootstrap 5 |
| 데이터베이스 | TiDB (MySQL 호환) |
| 에디터 | Marked.js + Quill.js |

---

## License

[MIT License](LICENSE)

## Contributing

Issues and Pull Requests are welcome!

---

<div align="center">

**If you like this project, please give it a ⭐!**

</div>
