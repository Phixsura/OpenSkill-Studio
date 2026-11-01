"use client";

interface ActivityIndicatorProps { status: string; label: string; dot: string;
  showLabel?: boolean; size?: "sm" | "md"; }

export function ActivityIndicator({ status, label, dot, showLabel = true, size = "md" }: ActivityIndicatorProps) {
  const dotSize = size === "sm" ? "text-xs" : "text-sm";
  return (
    <span className="inline-flex items-center gap-1">
      <span className={dotSize}>{dot}</span>
      {showLabel && <span className="text-xs text-gray-400">{label}</span>}
    </span>
  );
}
