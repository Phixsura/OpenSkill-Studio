"use client";

interface StatusIndicatorProps { status: string; label: string; icon: string; color: string;
  appName: string; isHealthy: boolean; }

const dotColors: Record<string, string> = {
  green: "bg-green-500", red: "bg-red-500", yellow: "bg-yellow-500",
  blue: "bg-blue-500", orange: "bg-orange-500",
};

export function StatusIndicator({ status, label, icon, color, appName, isHealthy }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className={`h-2.5 w-2.5 rounded-full ${dotColors[color] ?? "bg-gray-400"} ${!isHealthy && status !== "maintenance" ? "animate-pulse" : ""}`} />
      <span className="text-sm font-medium">{appName || label}</span>
      <span className="text-xs text-gray-400">{icon} {label}</span>
    </div>
  );
}
