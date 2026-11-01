"use client";

interface StatusIndicatorDotProps { status: string; label: string; icon: string;
  healthyCount?: number; totalCount?: number; showLabel?: boolean; }

export function StatusIndicatorDot({ status, label, icon, healthyCount, totalCount, showLabel = true }: StatusIndicatorDotProps) {
  const pulseClass = status === "operational" ? "" : "animate-pulse";
  return (
    <div className="flex items-center gap-2">
      <span className={`text-lg ${pulseClass}`}>{icon}</span>
      {showLabel && (
        <div>
          <p className="text-sm font-medium">{label}</p>
          {healthyCount !== undefined && totalCount !== undefined && (
            <p className="text-xs text-gray-400">{healthyCount}/{totalCount} healthy</p>
          )}
        </div>
      )}
    </div>
  );
}
