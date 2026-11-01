"use client";

interface FunctionStat { function: string; count: number; successRate: number; avgMs: number; uniqueErrors: number; }

interface FunctionStatsTableProps { stats: FunctionStat[]; }

export function FunctionStatsTable({ stats }: FunctionStatsTableProps) {
  if (stats.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No execution data</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-3 py-2">Function</th><th className="px-3 py-2">Calls</th>
          <th className="px-3 py-2">Success</th><th className="px-3 py-2">Avg Latency</th><th className="px-3 py-2">Errors</th>
        </tr></thead>
        <tbody>{stats.map(s => (
          <tr key={s.function} className="border-b dark:border-gray-800">
            <td className="px-3 py-2 font-mono text-xs">{s.function}</td>
            <td className="px-3 py-2">{s.count}</td>
            <td className={`px-3 py-2 ${s.successRate >= 95 ? "text-green-600" : s.successRate >= 80 ? "text-yellow-600" : "text-red-600"}`}>{s.successRate}%</td>
            <td className="px-3 py-2">{s.avgMs}ms</td>
            <td className="px-3 py-2">{s.uniqueErrors > 0 ? <span className="text-red-500">{s.uniqueErrors}</span> : "—"}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}
