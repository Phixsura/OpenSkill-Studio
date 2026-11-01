"use client";

interface PipelineStatusCardProps {
  name: string; status: string; transformCount: number;
  lastRunAt?: string; successRate: number;
}

export function PipelineStatusCard({ name, status, transformCount, lastRunAt, successRate }: PipelineStatusCardProps) {
  const statusColors: Record<string, string> = {
    running: "text-blue-600", success: "text-green-600", failed: "text-red-600", created: "text-gray-500",
  };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{name}</h3>
        <span className={`text-sm font-medium ${statusColors[status] || ""}`}>{status}</span>
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
        <div><p className="font-bold">{transformCount}</p><p className="text-gray-400">Steps</p></div>
        <div><p className="font-bold">{successRate}%</p><p className="text-gray-400">Success</p></div>
        <div><p className="font-bold">{lastRunAt?.slice(0, 10) || "—"}</p><p className="text-gray-400">Last Run</p></div>
      </div>
    </div>
  );
}
