#!/bin/bash
# 会话保活脚本 (iTerm2 版)
# 一启动就发"继续" + 触发 Loom，之后每5秒检测 Loom，每28分钟发继续
#
# 用法: 在 iTerm2 新 tab 里运行
#   ./scripts/keep-session-alive.sh [claude所在tab索引，默认0]

LOOM_CHECK_INTERVAL=5
CLAUDE_INTERVAL=1680
CLAUDE_COUNTER=0
CLAUDE_TAB=$((${1:-0} + 1))  # AppleScript tab 从1开始

echo "🚀 保活脚本启动 — $(date)"
echo "   Claude tab: 第${CLAUDE_TAB}个"
echo ""

# ====== 启动时立即执行一次 ======
echo "[$(date '+%H:%M:%S')] 🔄 立即发送 '继续' 到 Claude tab ${CLAUDE_TAB}..."
osascript -e "
tell application \"iTerm2\"
    tell current window
        tell tab ${CLAUDE_TAB}
            tell current session
                write text \"继续\"
            end tell
        end tell
    end tell
end tell
" 2>&1
if [ $? -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] ✅ '继续' 已发送"
else
    echo "[$(date '+%H:%M:%S')] ❌ 发送失败！检查 tab 索引"
fi

echo ""
echo "[$(date '+%H:%M:%S')] 🎥 立即触发 Loom 录制..."
# 先确保 Loom 在运行
if ! pgrep -ix "Loom" > /dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] Loom 未运行，启动中..."
    open -a "Loom"
    sleep 5
fi
# 用 Loom 的 URL scheme 尝试触发录制
open "loom-record://" 2>/dev/null
# 同时尝试快捷键
sleep 1
osascript -e 'tell application "System Events" to keystroke "l" using {command down, shift down}' 2>&1
if [ $? -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] ✅ Loom 录制命令已发送"
else
    echo "[$(date '+%H:%M:%S')] ⚠️ Loom 快捷键发送失败"
fi

echo ""
echo "====== 持续监控中 (Ctrl+C 停止) ======"
echo ""

# ====== 持续循环 ======
while true; do
    sleep $LOOM_CHECK_INTERVAL
    CLAUDE_COUNTER=$((CLAUDE_COUNTER + LOOM_CHECK_INTERVAL))

    # 每5秒：检测 Loom
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] ❌ Loom 挂了！重启..."
        open -a "Loom"
        sleep 5
        open "loom-record://" 2>/dev/null
        sleep 1
        osascript -e 'tell application "System Events" to keystroke "l" using {command down, shift down}' 2>/dev/null
        echo "[$(date '+%H:%M:%S')] ✅ Loom 已重启+录制"
    fi

    # 每28分钟：发"继续"
    if [ $CLAUDE_COUNTER -ge $CLAUDE_INTERVAL ]; then
        CLAUDE_COUNTER=0
        echo "[$(date '+%H:%M:%S')] 🔄 发送 '继续'..."
        osascript -e "
tell application \"iTerm2\"
    tell current window
        tell tab ${CLAUDE_TAB}
            tell current session
                write text \"继续\"
            end tell
        end tell
    end tell
end tell
" 2>/dev/null
        echo "[$(date '+%H:%M:%S')] ✅ 已发送"
    fi
done
