"use client";

interface MetricCardProps { label: string; display: string; unit: string;
  trend: "up" | "down" | "flat" | null; changePct: number | null; }

const trendConfig = {
  up: { icon: "↑", color: "text-green-600" },
  down: { icon: "↓", color: "text-red-600" },
  flat: { icon: "→", color: "text-gray-400" },
};

export function MetricCard({ label, display, unit, trend, changePct }: MetricCardProps) {
  const t = trend ? trendConfig[trend] : null;
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
      <div className="mt-2 flex items-baseline gap-1.5">
        <span className="text-2xl font-bold">{display}</span>
        {unit && <span className="text-sm text-gray-400">{unit}</span>}
      </div>
      {t && changePct !== null && (
        <div className={`mt-1.5 flex items-center gap-1 text-xs ${t.color}`}>
          <span>{t.icon}</span>
          <span>{Math.abs(changePct)}%</span>
          <span className="text-gray-400">vs prev</span>
        </div>
      )}
    </div>
  );
}
