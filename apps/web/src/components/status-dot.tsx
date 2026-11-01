"use client";

interface StatusDotProps { status: string; label: string; icon: string; showLabel?: boolean; }

const DOT_COLOR: Record<string, string> = {
  green: "bg-green-500", yellow: "bg-yellow-500", orange: "bg-orange-500",
  red: "bg-red-500", blue: "bg-blue-500", gray: "bg-gray-400",
};

export function StatusDot({ status, label, icon, showLabel = true }: StatusDotProps) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`w-2.5 h-2.5 rounded-full ${DOT_COLOR[status] || DOT_COLOR.gray}`} title={label} />
      {showLabel && <span className="text-xs text-gray-500">{label}</span>}
    </span>
  );
}
