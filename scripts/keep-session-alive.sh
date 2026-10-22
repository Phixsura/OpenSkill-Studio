#!/bin/bash
# 会话保活脚本 (iTerm2 版)
# - 每5秒检测 Loom
# - 每28分钟给 Claude 发"继续"（通过 iTerm2 AppleScript）
#
# 用法: 在 iTerm2 的【另一个tab】运行
#   ./scripts/keep-session-alive.sh
#
# 注意: Claude Code 必须在 iTerm2 的第一个 tab 运行

LOOM_CHECK_INTERVAL=5
CLAUDE_INTERVAL=1680  # 28分钟
CLAUDE_COUNTER=0
# Claude 所在的 tab 索引 (0 = 第一个 tab)
CLAUDE_TAB_INDEX="${1:-0}"

echo "🚀 会话保活脚本 (iTerm2) — $(date)"
echo "   Loom 检测: 每5秒"
echo "   Claude 继续: 每28分钟"
echo "   Claude tab: 第$((CLAUDE_TAB_INDEX+1))个tab"
echo "   Ctrl+C 停止"
echo ""

send_continue_iterm2() {
    osascript <<APPLESCRIPT
tell application "iTerm2"
    tell current window
        tell tab $((CLAUDE_TAB_INDEX+1))
            tell current session
                write text "继续"
            end tell
        end tell
    end tell
end tell
APPLESCRIPT
}

restart_loom_recording() {
    osascript -e 'tell application "System Events" to keystroke "l" using {command down, shift down}' 2>/dev/null
}

while true; do
    sleep $LOOM_CHECK_INTERVAL
    CLAUDE_COUNTER=$((CLAUDE_COUNTER + LOOM_CHECK_INTERVAL))

    # ====== 每5秒：检测 Loom ======
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] ❌ Loom 未运行！启动中..."
        open -a "Loom"
        sleep 5
        echo "[$(date '+%H:%M:%S')] 🎥 启动录制..."
        sleep 3
        restart_loom_recording
        echo "[$(date '+%H:%M:%S')] ✅ Loom 录制已启动"
    fi

    # ====== 每28分钟：iTerm2 发"继续" ======
    if [ $CLAUDE_COUNTER -ge $CLAUDE_INTERVAL ]; then
        CLAUDE_COUNTER=0
        echo ""
        echo "[$(date '+%H:%M:%S')] 🔄 通过 iTerm2 发送 '继续'..."
        if send_continue_iterm2 2>/dev/null; then
            echo "[$(date '+%H:%M:%S')] ✅ 已发送"
        else
            echo "[$(date '+%H:%M:%S')] ⚠️ 发送失败，请确认 iTerm2 窗口和 tab"
        fi
        echo ""
    fi
done
