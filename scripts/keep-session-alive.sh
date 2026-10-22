#!/bin/bash
# 组合脚本：Claude 保活 + Loom 重录
# 用法: ./scripts/keep-session-alive.sh [tmux-session-name]
#
# 前置条件:
#   1. Claude Code 在 tmux session 里运行
#   2. Loom 已安装
#   3. 在另一个终端窗口运行此脚本
#
# 如果不用 tmux，可以改用 iTerm2 AppleScript 方式（见下方注释）

CLAUDE_INTERVAL=1680  # 28分钟
LOOM_INTERVAL=300     # 5分钟
TMUX_SESSION="${1:-0}" # tmux session 名称，默认 0
COUNTER=0

echo "🚀 会话保活脚本启动 — $(date)"
echo "   Claude 继续: 每28分钟"
echo "   Loom 检测:   每5分钟"
echo "   tmux session: $TMUX_SESSION"
echo "   按 Ctrl+C 停止"
echo ""

send_continue_to_claude() {
    # 方法1: tmux (推荐)
    if command -v tmux &>/dev/null && tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        tmux send-keys -t "$TMUX_SESSION" "继续" Enter
        echo "[$(date '+%H:%M:%S')] ✅ 已通过 tmux 发送 '继续'"
        return
    fi

    # 方法2: iTerm2 AppleScript (如果不用 tmux)
    # osascript -e '
    # tell application "iTerm2"
    #     tell current session of current window
    #         write text "继续"
    #     end tell
    # end tell
    # ' 2>/dev/null && echo "[$(date '+%H:%M:%S')] ✅ 已通过 iTerm2 发送" && return

    echo "[$(date '+%H:%M:%S')] ⚠️ 无法自动发送，请手动在 Claude 终端输入 '继续'"
}

check_loom() {
    # 检查 Loom 是否在运行
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] 🎥 Loom 未运行，启动中..."
        open -a "Loom" 2>/dev/null
        sleep 3
    fi

    # 发送 Loom 录制快捷键 (默认 Cmd+Shift+L)
    # 注意: 如果你的 Loom 快捷键不同，请修改这里
    osascript -e '
    tell application "System Events"
        keystroke "l" using {command down, shift down}
    end tell
    ' 2>/dev/null

    echo "[$(date '+%H:%M:%S')] 🎥 Loom 录制检测完成"
}

while true; do
    sleep $LOOM_INTERVAL
    COUNTER=$((COUNTER + LOOM_INTERVAL))

    # 每5分钟：检测 Loom
    check_loom

    # 每28分钟：发送"继续"给 Claude
    if [ $COUNTER -ge $CLAUDE_INTERVAL ]; then
        COUNTER=0
        echo ""
        echo "[$(date '+%H:%M:%S')] 🔄 发送 '继续' 到 Claude..."
        send_continue_to_claude
        echo ""
    fi

    REMAINING=$(( (CLAUDE_INTERVAL - COUNTER) / 60 ))
    echo "[$(date '+%H:%M:%S')] 下次: Loom 5分钟 | Claude ${REMAINING}分钟后"
done
