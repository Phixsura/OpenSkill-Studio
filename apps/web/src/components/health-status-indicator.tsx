"use client";

interface HealthStatusIndicatorProps { status: "healthy" | "warning" | "critical"; label?: string; size?: "sm" | "md" | "lg"; }

const STATUS_CONFIG = {
  healthy: { color: "bg-green-500", ring: "ring-green-200", icon: "✅", text: "text-green-700" },
  warning: { color: "bg-yellow-500", ring: "ring-yellow-200", icon: "⚠️", text: "text-yellow-700" },
  critical: { color: "bg-red-500", ring: "ring-red-200", icon: "🔴", text: "text-red-700" },
};

const SIZES = { sm: "h-2 w-2", md: "h-3 w-3", lg: "h-4 w-4" };

export function HealthStatusIndicator({ status, label, size = "md" }: HealthStatusIndicatorProps) {
  const cfg = STATUS_CONFIG[status];
  return (
    <div className="inline-flex items-center gap-2">
      <span className={`${SIZES[size]} rounded-full ${cfg.color} ring-2 ${cfg.ring} animate-pulse`} />
      {label && <span className={`text-sm font-medium ${cfg.text}`}>{label}</span>}
    </div>
  );
}
