"use client";

interface ApiStatusWidgetProps { status: string; icon: string;
  healthDisplay: string; latencyDisplay: string; }

export function ApiStatusWidget({ status, icon, healthDisplay, latencyDisplay }: ApiStatusWidgetProps) {
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
      status === "operational" ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400" :
      status === "degraded" ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20" :
      "bg-red-100 text-red-700 dark:bg-red-900/20"
    }`}>
      <span>{icon}</span>
      <span className="capitalize">{status}</span>
      <span className="text-gray-400">·</span>
      <span>{healthDisplay}</span>
      <span className="text-gray-400">·</span>
      <span>{latencyDisplay}</span>
    </div>
  );
}
