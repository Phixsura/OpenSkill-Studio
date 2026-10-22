"use client";

interface HealthTrendIndicatorProps { trend: string; current: number; change: number; }

export function HealthTrendIndicator({ trend, current, change }: HealthTrendIndicatorProps) {
  const icon = trend === "improving" ? "📈" : trend === "declining" ? "📉" : "➡️";
  const color = trend === "improving" ? "text-green-600" : trend === "declining" ? "text-red-600" : "text-gray-500";
  const changeText = change > 0 ? `+${change}` : `${change}`;
  return (
    <span className={`inline-flex items-center gap-1 text-sm ${color}`}>
      {icon} {current}% <span className="text-xs">({changeText})</span>
    </span>
  );
}
