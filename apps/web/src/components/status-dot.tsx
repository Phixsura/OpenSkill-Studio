"use client";

interface StatusDotProps { color: string; label: string; pulse: boolean; showLabel?: boolean; size?: "sm" | "md" | "lg"; }

const colorMap: Record<string, string> = {
  green: "bg-green-500", gray: "bg-gray-400", yellow: "bg-yellow-500",
  red: "bg-red-500", blue: "bg-blue-500",
};
const sizeMap: Record<string, string> = { sm: "h-2 w-2", md: "h-2.5 w-2.5", lg: "h-3 w-3" };

export function StatusDot({ color, label, pulse, showLabel = true, size = "md" }: StatusDotProps) {
  return (
    <div className="inline-flex items-center gap-1.5">
      <span className={`rounded-full ${sizeMap[size]} ${colorMap[color] ?? colorMap.gray} ${pulse ? "animate-pulse" : ""}`} />
      {showLabel && <span className="text-xs text-gray-500">{label}</span>}
    </div>
  );
}
