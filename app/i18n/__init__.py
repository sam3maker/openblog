import json
import os
from flask import session, request, current_app

_translations = {}
_supported_languages = ['zh', 'en', 'ja', 'ko', 'fr', 'de', 'es']
_default_language = 'zh'


def _load_translations():
    """加载所有语言文件"""
    global _translations
    if _translations:
        return _translations
    i18n_dir = os.path.join(os.path.dirname(__file__))
    for lang in _supported_languages:
        filepath = os.path.join(i18n_dir, f'{lang}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                _translations[lang] = json.load(f)
        else:
            _translations[lang] = {}
    return _translations


def get_language():
    """获取当前语言"""
    lang = session.get('language')
    if not lang:
        lang = request.accept_languages.best_match(_supported_languages) or _default_language
    return lang


def set_language(lang):
    """设置语言"""
    if lang in _supported_languages:
        session['language'] = lang


def t(key, **kwargs):
    """翻译文本"""
    lang = get_language()
    _load_translations()
    text = _translations.get(lang, {}).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_all_translations():
    """获取当前语言的全部翻译"""
    lang = get_language()
    _load_translations()
    return _translations.get(lang, {})


def get_supported_languages():
    """获取支持的语言列表"""
    return [
        {'code': 'zh', 'name': '中文', 'flag': '🇨🇳'},
        {'code': 'en', 'name': 'English', 'flag': '🇺🇸'},
        {'code': 'ja', 'name': '日本語', 'flag': '🇯🇵'},
        {'code': 'ko', 'name': '한국어', 'flag': '🇰🇷'},
        {'code': 'fr', 'name': 'Français', 'flag': '🇫🇷'},
        {'code': 'de', 'name': 'Deutsch', 'flag': '🇩🇪'},
        {'code': 'es', 'name': 'Español', 'flag': '🇪🇸'},
    ]
