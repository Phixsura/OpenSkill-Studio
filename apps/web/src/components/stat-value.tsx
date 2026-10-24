"use client";

interface StatValueProps { value: string | number; label: string; icon?: string; trend?: { direction: "up" | "down" | "flat"; pct: number }; size?: "sm" | "md" | "lg"; }

const TREND_CONFIG = {
  up: { icon: "↑", color: "text-green-600" },
  down: { icon: "↓", color: "text-red-600" },
  flat: { icon: "→", color: "text-gray-400" },
};

const SIZE_CLASSES = { sm: "text-lg", md: "text-2xl", lg: "text-4xl" };

export function StatValue({ value, label, icon, trend, size = "md" }: StatValueProps) {
  return (
    <div className="text-center">
      {icon && <span className="text-xl">{icon}</span>}
      <p className={`font-bold ${SIZE_CLASSES[size]}`}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
      <p className="text-xs text-gray-400">{label}</p>
      {trend && (
        <p className={`text-xs ${TREND_CONFIG[trend.direction].color}`}>
          {TREND_CONFIG[trend.direction].icon} {trend.pct}%
        </p>
      )}
    </div>
  );
}
