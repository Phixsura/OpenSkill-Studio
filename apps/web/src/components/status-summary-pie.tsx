"use client";

interface StatusSummaryPieProps { byStatus: Record<string, number>; total: number; }

const STATUS_COLORS: Record<string, string> = { published: "bg-green-500", draft: "bg-gray-400", testing: "bg-blue-400", submitted: "bg-purple-400", approved: "bg-cyan-400", deprecated: "bg-orange-400", revoked: "bg-red-500", rejected: "bg-red-400" };

export function StatusSummaryPie({ byStatus, total }: StatusSummaryPieProps) {
  if (total === 0) return <p className="py-3 text-center text-sm text-gray-400">No apps</p>;
  return (
    <div className="space-y-2">
      {Object.entries(byStatus).map(([status, count]) => (
        <div key={status} className="flex items-center gap-2 text-sm">
          <div className={`h-3 w-3 rounded-full ${STATUS_COLORS[status] ?? "bg-gray-300"}`} />
          <span className="flex-1 capitalize">{status}</span>
          <span className="font-medium">{count}</span>
          <span className="w-12 text-right text-xs text-gray-400">{Math.round(count / total * 100)}%</span>
        </div>
      ))}
    </div>
  );
}
