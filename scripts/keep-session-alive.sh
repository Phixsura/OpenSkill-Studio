#!/bin/bash
# 会话保活脚本 (iTerm2 版)
# - 每15分钟(+随机0-120秒) 给 Claude 发"继续"
# - 每5秒检测 Loom
# - 详细日志
#
# 用法: 在 iTerm2 新 tab 里运行
#   ./scripts/keep-session-alive.sh [claude所在tab索引，默认0]

LOOM_CHECK_INTERVAL=5
CLAUDE_BASE_INTERVAL=900  # 15分钟
CLAUDE_COUNTER=0
CLAUDE_TAB=$((${1:-0} + 1))
TOTAL_CONTINUES=0
TOTAL_LOOM_RESTARTS=0
START_TIME=$(date +%s)

# 随机延迟 0-120秒
random_delay() {
    echo $((RANDOM % 120))
}

CLAUDE_INTERVAL=$((CLAUDE_BASE_INTERVAL + $(random_delay)))

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 =============================="
log "🚀 会话保活脚本启动"
log "🚀 =============================="
log "📋 配置:"
log "   Loom 检测间隔: ${LOOM_CHECK_INTERVAL}秒"
log "   Claude 继续间隔: ~15分钟 (当前: ${CLAUDE_INTERVAL}秒)"
log "   Claude tab: 第${CLAUDE_TAB}个"
log "   PID: $$"
log ""

# ====== 启动时立即执行 ======
log "🔄 [初始化] 发送 '继续' 到 Claude tab ${CLAUDE_TAB}..."
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
    TOTAL_CONTINUES=$((TOTAL_CONTINUES + 1))
    log "✅ [初始化] '继续' 发送成功 (累计: ${TOTAL_CONTINUES}次)"
else
    log "❌ [初始化] '继续' 发送失败！检查 tab 索引"
fi

log ""
log "🎥 [初始化] 检测 Loom..."
if pgrep -ix "Loom" > /dev/null 2>&1; then
    log "✅ Loom 正在运行 (PID: $(pgrep -ix 'Loom' | head -1))"
else
    log "⚠️ Loom 未运行，启动中..."
    open -a "Loom"
    sleep 5
    log "✅ Loom 已启动"
fi

log "🎥 [初始化] 触发 Loom 录制..."
osascript -e '
tell application "System Events"
    tell process "Loom"
        set frontmost to true
    end tell
    delay 0.5
    keystroke "l" using {command down, shift down}
end tell
' 2>/dev/null
sleep 2
# 发 Enter 点 Continue
osascript -e '
tell application "System Events"
    key code 36
end tell
' 2>/dev/null
log "✅ [初始化] Loom 录制命令已发送"

log ""
log "====== 持续监控中 (Ctrl+C 停止) ======"
log ""

# ====== 主循环 ======
while true; do
    sleep $LOOM_CHECK_INTERVAL
    CLAUDE_COUNTER=$((CLAUDE_COUNTER + LOOM_CHECK_INTERVAL))
    UPTIME=$(( $(date +%s) - START_TIME ))
    UPTIME_MIN=$((UPTIME / 60))

    # 每5秒：检测 Loom（静默，只有异常才输出）
    if ! pgrep -ix "Loom" > /dev/null 2>&1; then
        TOTAL_LOOM_RESTARTS=$((TOTAL_LOOM_RESTARTS + 1))
        log "❌ [Loom] 进程不存在！第${TOTAL_LOOM_RESTARTS}次重启..."
        open -a "Loom"
        sleep 5
        osascript -e '
tell application "System Events"
    tell process "Loom"
        set frontmost to true
    end tell
    delay 0.5
    keystroke "l" using {command down, shift down}
end tell
' 2>/dev/null
        sleep 2
        osascript -e 'tell application "System Events" to key code 36' 2>/dev/null
        log "✅ [Loom] 重启+录制完成"
    fi

    # 每~15分钟(+随机)：发"继续"
    if [ $CLAUDE_COUNTER -ge $CLAUDE_INTERVAL ]; then
        CLAUDE_COUNTER=0
        CLAUDE_INTERVAL=$((CLAUDE_BASE_INTERVAL + $(random_delay)))  # 重新随机
        TOTAL_CONTINUES=$((TOTAL_CONTINUES + 1))

        log ""
        log "📊 ====== 状态报告 ======"
        log "   运行时间: ${UPTIME_MIN}分钟"
        log "   累计发送继续: ${TOTAL_CONTINUES}次"
        log "   Loom 重启次数: ${TOTAL_LOOM_RESTARTS}次"
        log "   下次继续间隔: ${CLAUDE_INTERVAL}秒"
        log ""
        log "🔄 [Claude] 发送 '继续'..."

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

        if [ $? -eq 0 ]; then
            log "✅ [Claude] '继续' 已发送 (第${TOTAL_CONTINUES}次)"
        else
            log "❌ [Claude] 发送失败"
        fi
        log ""
    fi
done
