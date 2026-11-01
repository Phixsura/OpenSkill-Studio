"use client";

interface MetricCardProps { label: string; display: string; icon: string;
  deltaDisplay: string | null; trend: string | null; unit: string; }

export function MetricCard({ label, display, icon, deltaDisplay, trend, unit }: MetricCardProps) {
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-1">
        <span className="text-lg">{icon}</span>
        {deltaDisplay && (
          <span className={`text-xs font-medium ${trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-gray-400"}`}>
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {deltaDisplay}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold">{display}{unit && <span className="text-sm text-gray-400 ml-0.5">{unit}</span>}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  );
}
