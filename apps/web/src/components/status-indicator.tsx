"use client";

interface StatusIndicatorProps { status: "operational" | "degraded" | "outage" | "maintenance"; label?: string; }

const STYLES: Record<string, { dot: string; text: string }> = {
  operational: { dot: "bg-green-500", text: "text-green-700" },
  degraded: { dot: "bg-yellow-500", text: "text-yellow-700" },
  outage: { dot: "bg-red-500", text: "text-red-700" },
  maintenance: { dot: "bg-blue-500", text: "text-blue-700" },
};

export function StatusIndicator({ status, label }: StatusIndicatorProps) {
  const s = STYLES[status] ?? STYLES.operational;
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`h-2 w-2 rounded-full ${s.dot}`} />
      <span className={`text-sm capitalize ${s.text}`}>{label ?? status}</span>
    </span>
  );
}
