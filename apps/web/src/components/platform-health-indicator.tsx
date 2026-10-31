"use client";

interface PlatformHealthIndicatorProps {
  health: "healthy" | "degraded" | "critical";
  errorRate: number;
  pendingReviews: number;
}

const HEALTH_STYLES: Record<string, { icon: string; bg: string; text: string }> = {
  healthy: { icon: "💚", bg: "bg-green-50 border-green-200 dark:bg-green-900/20", text: "All systems operational" },
  degraded: { icon: "⚠️", bg: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20", text: "Some issues detected" },
  critical: { icon: "🚨", bg: "bg-red-50 border-red-200 dark:bg-red-900/20", text: "Critical issues" },
};

export function PlatformHealthIndicator({ health, errorRate, pendingReviews }: PlatformHealthIndicatorProps) {
  const style = HEALTH_STYLES[health] ?? HEALTH_STYLES.healthy;
  return (
    <div className={`rounded-lg border p-4 ${style.bg}`}>
      <div className="flex items-center gap-2">
        <span className="text-2xl">{style.icon}</span>
        <div>
          <p className="font-semibold">{style.text}</p>
          <p className="text-xs text-gray-500">Error rate: {errorRate}% · {pendingReviews} pending review{pendingReviews !== 1 ? "s" : ""}</p>
        </div>
      </div>
    </div>
  );
}
