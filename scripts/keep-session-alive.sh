#!/bin/bash
# 会话保活脚本：5秒检测一次
# - 检测 Loom 是否在运行，不在就重启
# - 每28分钟给 Claude 发"继续"
#
# 用法: ./scripts/keep-session-alive.sh [tmux-session-name]

LOOM_CHECK_INTERVAL=5    # 5秒检测一次
CLAUDE_INTERVAL=1680     # 28分钟
CLAUDE_COUNTER=0
TMUX_SESSION="${1:-0}"

echo "🚀 会话保活脚本 — $(date)"
echo "   Loom 检测: 每5秒"
echo "   Claude 继续: 每28分钟"
echo "   tmux: $TMUX_SESSION"
echo "   Ctrl+C 停止"
echo ""

restart_loom_recording() {
    # 方法1: 用 Loom 的全局快捷键重新开始录制
    osascript <<'APPLESCRIPT'
tell application "System Events"
    -- Loom 默认录制快捷键 Cmd+Shift+L
    keystroke "l" using {command down, shift down}
end tell
APPLESCRIPT
}

while true; do
    sleep $LOOM_CHECK_INTERVAL
    CLAUDE_COUNTER=$((CLAUDE_COUNTER + LOOM_CHECK_INTERVAL))

    # ====== 每5秒：检测 Loom ======
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] ❌ Loom 未运行！正在启动..."
        open -a "Loom"
        sleep 5
        echo "[$(date '+%H:%M:%S')] 🎥 Loom 已启动，等待3秒后开始录制..."
        sleep 3
        restart_loom_recording
        echo "[$(date '+%H:%M:%S')] ✅ Loom 录制已启动"
    fi

    # ====== 每28分钟：给 Claude 发"继续" ======
    if [ $CLAUDE_COUNTER -ge $CLAUDE_INTERVAL ]; then
        CLAUDE_COUNTER=0
        echo ""
        echo "[$(date '+%H:%M:%S')] 🔄 发送 '继续' 到 Claude (tmux: $TMUX_SESSION)..."

        if command -v tmux &>/dev/null && tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
            tmux send-keys -t "$TMUX_SESSION" "继续" Enter
            echo "[$(date '+%H:%M:%S')] ✅ 已发送"
        else
            echo "[$(date '+%H:%M:%S')] ⚠️ tmux session '$TMUX_SESSION' 不存在"
            # 列出可用的 tmux sessions
            echo "   可用 sessions:"
            tmux list-sessions 2>/dev/null || echo "   (无)"
        fi
        echo ""
    fi
done
