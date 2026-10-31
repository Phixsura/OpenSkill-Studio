#!/bin/bash
# 会话保活脚本 (iTerm2 版)
# - 每5秒检测 Loom 是否在录制（不是检测进程，是检测窗口数）
# - 不在录制就重新触发录制
# - 每15分钟(+随机0-120秒) 给 Claude 发"继续"
#
# 用法: ./scripts/keep-session-alive.sh [claude所在tab索引，默认0]

LOOM_CHECK_INTERVAL=5
CLAUDE_BASE_INTERVAL=900
CLAUDE_COUNTER=0
CLAUDE_TAB=$((${1:-0} + 1))
TOTAL_CONTINUES=0
TOTAL_LOOM_RESTARTS=0
START_TIME=$(date +%s)

random_delay() { echo $((RANDOM % 120)); }
CLAUDE_INTERVAL=$((CLAUDE_BASE_INTERVAL + $(random_delay)))

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

is_loom_recording() {
    # 检测 Loom 窗口数 — 录制时有窗口，不录制时0个窗口
    local window_count
    window_count=$(osascript -e '
tell application "System Events"
    if not (exists process "Loom") then return "0"
    tell process "Loom"
        return (count of windows) as text
    end tell
end tell
' 2>/dev/null)
    [ "${window_count:-0}" -gt 0 ] 2>/dev/null
}

start_loom_recording() {
    log "🎥 触发 Loom 录制..."

    # 确保 Loom 进程在运行
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        log "   Loom 进程不存在，启动中..."
        open -a "Loom"
        sleep 5
    fi

    # 激活 Loom 并发快捷键
    osascript -e '
tell application "System Events"
    tell process "Loom"
        set frontmost to true
    end tell
    delay 0.5
    keystroke "l" using {command down, shift down}
end tell
' 2>/dev/null
    sleep 3

    # 按 Enter 跳过 Continue/确认界面
    osascript -e '
tell application "System Events"
    key code 36
end tell
' 2>/dev/null
    sleep 1
    osascript -e '
tell application "System Events"
    key code 36
end tell
' 2>/dev/null

    TOTAL_LOOM_RESTARTS=$((TOTAL_LOOM_RESTARTS + 1))
    log "✅ Loom 录制命令已发送 (第${TOTAL_LOOM_RESTARTS}次)"
}

send_continue() {
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
}

# ====== 启动 ======
log "🚀 =============================="
log "🚀 会话保活脚本启动"
log "🚀 =============================="
log "📋 配置:"
log "   Loom 录制检测: 每${LOOM_CHECK_INTERVAL}秒 (检测窗口数)"
log "   Claude 继续: ~15分钟+随机 (当前: ${CLAUDE_INTERVAL}秒)"
log "   Claude tab: 第${CLAUDE_TAB}个"
log ""

# 启动时立即发继续
log "🔄 [初始化] 发送 '继续'..."
if send_continue; then
    TOTAL_CONTINUES=$((TOTAL_CONTINUES + 1))
    log "✅ [初始化] '继续' 已发送"
else
    log "❌ [初始化] '继续' 发送失败"
fi

# 启动时检测并启动 Loom 录制
log ""
if is_loom_recording; then
    log "✅ [初始化] Loom 正在录制"
else
    log "⚠️ [初始化] Loom 未在录制"
    start_loom_recording
fi

log ""
log "====== 持续监控中 (Ctrl+C 停止) ======"
log ""

# ====== 主循环 ======
while true; do
    sleep $LOOM_CHECK_INTERVAL
    CLAUDE_COUNTER=$((CLAUDE_COUNTER + LOOM_CHECK_INTERVAL))

    # 每5秒：检测 Loom 录制状态
    if ! is_loom_recording; then
        log "❌ [Loom] 录制已停止！重新启动录制..."
        start_loom_recording
    fi

    # 每~15分钟：发"继续"
    if [ $CLAUDE_COUNTER -ge $CLAUDE_INTERVAL ]; then
        CLAUDE_COUNTER=0
        CLAUDE_INTERVAL=$((CLAUDE_BASE_INTERVAL + $(random_delay)))
        TOTAL_CONTINUES=$((TOTAL_CONTINUES + 1))
        UPTIME_MIN=$(( ($(date +%s) - START_TIME) / 60 ))

        log ""
        log "📊 ====== 状态报告 (运行${UPTIME_MIN}分钟) ======"
        log "   累计继续: ${TOTAL_CONTINUES}次 | Loom重启: ${TOTAL_LOOM_RESTARTS}次"
        log "   下次继续: ${CLAUDE_INTERVAL}秒后"
        log "🔄 [Claude] 发送 '继续'..."

        if send_continue; then
            log "✅ [Claude] 已发送 (第${TOTAL_CONTINUES}次)"
        else
            log "❌ [Claude] 发送失败"
        fi
        log ""
    fi
done
