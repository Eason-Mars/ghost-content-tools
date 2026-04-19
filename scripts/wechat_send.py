#!/usr/bin/env python3
"""
微信 UI 自动化发送消息脚本
依赖: pip3 install atomacos
权限: 系统设置 → 隐私与安全性 → 辅助功能 → 添加 Terminal/OpenClaw
"""

import atomacos
import time
import subprocess
import sys


def activate_wechat():
    """激活微信窗口"""
    subprocess.run(["osascript", "-e", 'tell application "WeChat" to activate'])
    time.sleep(0.8)


def get_wechat_app():
    """获取微信 App 引用"""
    try:
        return atomacos.getAppRefByBundleId("com.tencent.xinWeChat")
    except Exception as e:
        print(f"[错误] 无法访问微信: {e}")
        print("请确认已在【系统设置 → 辅助功能】中授权 Terminal/OpenClaw")
        sys.exit(1)


def list_chats(app):
    """列出聊天列表"""
    try:
        wins = app.windows()
        if not wins:
            print("[错误] 微信没有打开的窗口")
            return []

        main_win = wins[0]
        print(f"[主窗口] {main_win.AXTitle}")

        # 找聊天列表 (table/list 元素)
        chats = []
        try:
            # 遍历 UI 树找列表项
            groups = main_win.findAllR(AXRole="AXGroup")
            for g in groups[:5]:
                print(f"  Group: {g.AXRole} - {getattr(g, 'AXIdentifier', 'N/A')}")
        except Exception as e:
            print(f"  遍历 UI 失败: {e}")

        return chats
    except Exception as e:
        print(f"[错误] 读取聊天列表失败: {e}")
        return []


def send_message(target_name: str, message: str):
    """
    向指定联系人/群发送消息
    :param target_name: 聊天名称（好友昵称或群名）
    :param message: 消息内容
    """
    activate_wechat()
    app = get_wechat_app()

    try:
        wins = app.windows()
        if not wins:
            print("[错误] 微信没有打开的窗口")
            return False

        main_win = wins[0]

        # 方法1: 使用搜索框定位联系人
        # 找搜索框
        search_fields = main_win.findAllR(AXRole="AXTextField")
        search_box = None
        for field in search_fields:
            placeholder = getattr(field, "AXPlaceholderValue", "")
            if "搜索" in str(placeholder) or "Search" in str(placeholder):
                search_box = field
                break

        if not search_box:
            # 尝试用快捷键打开搜索
            subprocess.run(["osascript", "-e",
                'tell application "System Events" to keystroke "f" using command down'])
            time.sleep(0.5)
            search_fields = main_win.findAllR(AXRole="AXTextField")
            for field in search_fields:
                placeholder = getattr(field, "AXPlaceholderValue", "")
                if "搜索" in str(placeholder) or "Search" in str(placeholder):
                    search_box = field
                    break

        if search_box:
            # 点击搜索框，输入联系人名字
            search_box.AXFocused = True
            time.sleep(0.3)

            # 清空并输入
            search_box.AXValue = ""
            search_box.sendKeys(target_name)
            time.sleep(1.0)

            # 找搜索结果并点击第一个
            results = main_win.findAllR(AXRole="AXCell")
            if results:
                results[0].Press()
                time.sleep(0.5)
            else:
                print(f"[错误] 未找到联系人: {target_name}")
                return False
        else:
            print("[警告] 未找到搜索框，尝试直接找聊天")

        # 找消息输入框并发送
        text_areas = main_win.findAllR(AXRole="AXTextArea")
        input_box = None
        for ta in text_areas:
            desc = getattr(ta, "AXRoleDescription", "")
            if desc or ta.AXEnabled:
                input_box = ta
                break

        if not input_box:
            print("[错误] 未找到消息输入框")
            return False

        # 点击输入框，输入消息，发送
        input_box.AXFocused = True
        time.sleep(0.2)
        input_box.sendKeys(message)
        time.sleep(0.2)

        # 按回车发送
        subprocess.run(["osascript", "-e",
            'tell application "System Events" to key code 36'])
        time.sleep(0.3)

        print(f"[成功] 已向 '{target_name}' 发送: {message}")
        return True

    except Exception as e:
        print(f"[错误] 发送失败: {e}")
        return False


def dump_ui():
    """调试：输出微信 UI 树结构"""
    activate_wechat()
    app = get_wechat_app()

    wins = app.windows()
    print(f"找到 {len(wins)} 个窗口")
    for i, w in enumerate(wins[:2]):
        print(f"\n=== 窗口 {i}: {getattr(w, 'AXTitle', 'N/A')} ===")
        try:
            children = w.AXChildren
            for j, child in enumerate(children[:10]):
                role = getattr(child, "AXRole", "?")
                desc = getattr(child, "AXRoleDescription", "")
                title = getattr(child, "AXTitle", "")
                print(f"  [{j}] {role} | {desc} | {title}")
        except Exception as e:
            print(f"  读取子元素失败: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("用法:")
        print("  python3 wechat_send.py dump              # 查看 UI 树")
        print("  python3 wechat_send.py send '群名' '消息'  # 发送消息")
    elif sys.argv[1] == "dump":
        dump_ui()
    elif sys.argv[1] == "send" and len(sys.argv) >= 4:
        send_message(sys.argv[2], sys.argv[3])
    else:
        print("参数错误，运行不带参数查看用法")
