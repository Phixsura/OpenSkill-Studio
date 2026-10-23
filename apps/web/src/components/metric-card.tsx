"use client";

interface MetricCardProps { label: string; value: number; change: number | null;
  changePct: number | null; trend: string | null; formatType: string; icon: string; }

function fmt(val: number, type: string): string {
  if (type === "currency") return `$${val.toLocaleString()}`;
  if (type === "percentage") return `${val}%`;
  return val.toLocaleString();
}

export function MetricCard({ label, value, change, changePct, trend, formatType, icon }: MetricCardProps) {
  const trendIcon = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";
  const trendColor = trend === "up" ? "text-green-500" : trend === "down" ? "text-red-500" : "text-gray-400";
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-lg">{icon}</span>
      </div>
      <p className="mt-1 text-2xl font-bold">{fmt(value, formatType)}</p>
      {change !== null && changePct !== null && (
        <p className={`mt-0.5 text-xs ${trendColor}`}>
          {trendIcon} {Math.abs(change).toLocaleString()} ({changePct > 0 ? "+" : ""}{changePct}%)
        </p>
      )}
    </div>
  );
}
