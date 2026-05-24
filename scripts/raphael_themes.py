#!/usr/bin/env python3
"""
Raphael 主题库 - 微信公众号样式主题集合
"""

DEFAULT_THEME = 'eason'

# Eason 主题（默认）
EASON_THEME = {
    'container': 'font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 15px; line-height: 1.9; color: rgba(0,0,0,0.88); padding: 0; margin: 0;',
    'h1': 'font-size: 20px; font-weight: bold; color: #000; margin: 32px 0 16px; line-height: 1.5;',
    'h2': 'font-size: 18px; font-weight: bold; color: #000; margin: 28px 0 14px; line-height: 1.5;',
    'h3': 'font-size: 16px; font-weight: bold; color: #000; margin: 24px 0 12px; line-height: 1.5;',
    'h4': 'font-size: 15px; font-weight: bold; color: #000; margin: 20px 0 10px; line-height: 1.5;',
    'p': 'font-size: 15px; line-height: 1.9; color: rgba(0,0,0,0.88); margin-bottom: 20px;',
    'strong': 'font-weight: bold; color: rgba(0,0,0,0.88);',
    'em': 'font-style: italic; color: rgba(0,0,0,0.88);',
    'a': 'color: #1a73e8; text-decoration: none;',
    'ul': 'margin: 0 0 20px; padding-left: 0;',
    'ol': 'margin: 0 0 20px; padding-left: 0;',
    'li': 'font-size: 15px; line-height: 1.9; color: rgba(0,0,0,0.88); padding-left: 16px; margin-bottom: 8px;',
    'blockquote': 'font-size: 15px; line-height: 1.9; color: #555; background: #f9f9f9; padding: 16px 20px; margin: 20px 0; border-left: 4px solid #ddd;',
    'code': "font-family: 'SF Mono', Consolas, monospace; padding: 3px 6px; background: #f5f3f0; border-radius: 3px; font-size: 13px;",
    'pre': 'font-size: 13px; line-height: 1.8; color: #555; background: #f5f3f0; padding: 14px 18px; margin: 16px 0 24px; border-radius: 4px; white-space: pre-wrap; word-break: break-all;',
    'hr': 'border: none; border-top: 1px solid #e0e0e0; margin: 32px 0;',
    'img': 'max-width: 100%; height: auto; display: block; margin: 16px auto;',
    'table': 'width: 100%; border-collapse: collapse; margin: 16px 0;',
    'th': 'border: 1px solid #ddd; padding: 8px 12px; background: #f5f5f5; font-weight: bold;',
    'td': 'border: 1px solid #ddd; padding: 8px 12px;',
    'tr': 'border: 1px solid #ddd;',
}

# Claude 主题
CLAUDE_THEME = {
    'container': 'font-family: "Charter", Georgia, serif; font-size: 16px; line-height: 1.75; color: #1a1a1a; padding: 0; margin: 0;',
    'h1': 'font-size: 24px; font-weight: 600; color: #000; margin: 36px 0 18px; line-height: 1.4;',
    'h2': 'font-size: 20px; font-weight: 600; color: #000; margin: 32px 0 16px; line-height: 1.4;',
    'h3': 'font-size: 18px; font-weight: 600; color: #000; margin: 28px 0 14px; line-height: 1.4;',
    'h4': 'font-size: 16px; font-weight: 600; color: #000; margin: 24px 0 12px; line-height: 1.4;',
    'p': 'font-size: 16px; line-height: 1.75; color: #1a1a1a; margin-bottom: 24px;',
    'strong': 'font-weight: 600; color: #1a1a1a;',
    'em': 'font-style: italic; color: #1a1a1a;',
    'a': 'color: #0066cc; text-decoration: underline;',
    'ul': 'margin: 0 0 24px; padding-left: 0;',
    'ol': 'margin: 0 0 24px; padding-left: 0;',
    'li': 'font-size: 16px; line-height: 1.75; color: #1a1a1a; padding-left: 20px; margin-bottom: 10px;',
    'blockquote': 'font-size: 16px; line-height: 1.75; color: #4a4a4a; background: #fafafa; padding: 20px 24px; margin: 24px 0; border-left: 4px solid #ccc;',
    'code': "font-family: 'Fira Code', 'Courier New', monospace; padding: 3px 6px; background: #f4f4f4; border-radius: 3px; font-size: 14px;",
    'pre': 'font-size: 14px; line-height: 1.7; color: #333; background: #f4f4f4; padding: 16px 20px; margin: 20px 0 28px; border-radius: 4px; white-space: pre-wrap; word-break: break-all;',
    'hr': 'border: none; border-top: 2px solid #e8e8e8; margin: 36px 0;',
    'img': 'max-width: 100%; height: auto; display: block; margin: 20px auto;',
    'table': 'width: 100%; border-collapse: collapse; margin: 20px 0;',
    'th': 'border: 1px solid #ccc; padding: 10px 14px; background: #f0f0f0; font-weight: 600;',
    'td': 'border: 1px solid #ccc; padding: 10px 14px;',
    'tr': 'border: 1px solid #ccc;',
}

THEMES = {
    'eason': EASON_THEME,
    'claude': CLAUDE_THEME,
}


def get_theme(theme_id: str = DEFAULT_THEME) -> dict:
    """获取指定主题，不存在则返回默认主题"""
    return THEMES.get(theme_id, EASON_THEME)
