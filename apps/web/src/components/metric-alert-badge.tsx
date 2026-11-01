"use client";
interface MetricAlertBadgeProps { name: string; value: number; threshold: number; triggered: boolean; status: string; }
export function MetricAlertBadge({ name, value, threshold, triggered, status }: MetricAlertBadgeProps) {
  return (
    <div className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${triggered ? "border-red-300 bg-red-50 dark:bg-red-900/10" : "dark:border-gray-700"}`}>
      <span className={`h-2 w-2 rounded-full ${triggered ? "bg-red-500 animate-pulse" : "bg-green-500"}`} />
      <span className="text-sm font-medium">{name}</span>
      <span className="text-xs text-gray-400">{value} / {threshold}</span>
      <span className={`text-xs ${triggered ? "text-red-600" : "text-green-600"}`}>{status}</span>
    </div>
  );
}
