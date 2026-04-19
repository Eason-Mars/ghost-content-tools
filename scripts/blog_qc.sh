#!/bin/bash
# blog_qc.sh — Mars QC 检查 + 搬文件 + 推送（原子操作）
# 用法: bash blog_qc.sh <insight_output_file>

set -e

SRC="$1"
QUEUE_DIR="$HOME/.openclaw/workspace/personal-brand/content/queue"

if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "❌ 文件不存在: $SRC"
  exit 1
fi

FILENAME=$(basename "$SRC")
ERRORS=0

echo "🔍 QC 检查: $FILENAME"
echo "---"

# 1. 模板结构
for tag in '<nav' 'class="hero"' 'class="page"' 'class="closing"' 'class="x-box"' 'class="site-footer"'; do
  if ! grep -q "$tag" "$SRC"; then
    echo "❌ 缺少结构: $tag"
    ERRORS=$((ERRORS+1))
  fi
done
[ $ERRORS -eq 0 ] && echo "✅ 模板结构完整"

# 2. .label CSS
if ! grep -q 'h2 .label' "$SRC"; then
  echo "❌ 缺少 .label CSS"
  ERRORS=$((ERRORS+1))
else
  echo "✅ .label CSS 存在"
fi

# 3. closing 底色
if ! grep -q 'closing.*background.*#8B3A2A' "$SRC" && ! grep -q 'closing.*background: #8B3A2A' "$SRC"; then
  echo "❌ closing 底色不是 #8B3A2A"
  ERRORS=$((ERRORS+1))
else
  echo "✅ closing 底色正确"
fi

# 4. 签名
if ! grep -q '我叫 Eason' "$SRC"; then
  echo "❌ 签名 name 不对（应为「我叫 Eason」）"
  ERRORS=$((ERRORS+1))
else
  echo "✅ 签名正确"
fi

# 5. 乱码
if grep -q '��' "$SRC"; then
  echo "❌ 发现乱码（��）:"
  grep -n '��' "$SRC"
  ERRORS=$((ERRORS+1))
else
  echo "✅ 无乱码"
fi

# 6. 禁区词（排除 CSS 中的 Arial 等误报）
BODY_CONTENT=$(sed -n '/<body>/,/<\/body>/p' "$SRC")
if echo "$BODY_CONTENT" | grep -v 'font-family' | grep -qi '\bAMI\b\|ARTI\|杨国福'; then
  echo "⚠️ 可能有禁区词:"
  echo "$BODY_CONTENT" | grep -v 'font-family' | grep -in '\bAMI\b\|ARTI\|杨国福'
  ERRORS=$((ERRORS+1))
else
  echo "✅ 无禁区词"
fi

echo "---"

if [ $ERRORS -gt 0 ]; then
  echo "❌ QC 未通过（$ERRORS 项问题），不搬文件"
  exit 1
fi

echo "✅ QC 全部通过"

# 搬文件
cp "$SRC" "$QUEUE_DIR/$FILENAME"
echo "📁 已搬到: $QUEUE_DIR/$FILENAME"
echo "📤 路径: $QUEUE_DIR/$FILENAME"
