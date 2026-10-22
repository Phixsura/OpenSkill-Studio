"use client";

interface FnProfile { function: string; count: number; avgMs: number; p50Ms: number; p95Ms: number; minMs: number; maxMs: number; }

interface PerformanceProfileTableProps { profiles: FnProfile[]; }

export function PerformanceProfileTable({ profiles }: PerformanceProfileTableProps) {
  if (profiles.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No profiling data</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-2 py-1">Function</th><th className="px-2 py-1">Calls</th>
          <th className="px-2 py-1">Avg</th><th className="px-2 py-1">P50</th><th className="px-2 py-1">P95</th>
          <th className="px-2 py-1">Min</th><th className="px-2 py-1">Max</th>
        </tr></thead>
        <tbody>{profiles.map(p => (
          <tr key={p.function} className="border-b dark:border-gray-800">
            <td className="px-2 py-1 font-mono text-xs">{p.function}</td>
            <td className="px-2 py-1">{p.count}</td>
            <td className="px-2 py-1">{p.avgMs}ms</td>
            <td className="px-2 py-1">{p.p50Ms}ms</td>
            <td className={`px-2 py-1 ${p.p95Ms > 500 ? "text-red-600 font-medium" : ""}`}>{p.p95Ms}ms</td>
            <td className="px-2 py-1">{p.minMs}ms</td>
            <td className="px-2 py-1">{p.maxMs}ms</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}
