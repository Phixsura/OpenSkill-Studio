"use client";

interface ThrottleEntry { path: string; served: number; throttled: number; currentRpm: number; limit: number; }
interface ThrottleStatusTableProps { entries: ThrottleEntry[]; }

export function ThrottleStatusTable({ entries }: ThrottleStatusTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Throttle Status</h3>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Endpoint</th>
          <th className="p-3 text-right">RPM</th>
          <th className="p-3 text-right">Limit</th>
          <th className="p-3 text-right">Served</th>
          <th className="p-3 text-right">Throttled</th>
        </tr></thead>
        <tbody>
          {entries.map(e => {
            const pct = Math.round((e.currentRpm / Math.max(e.limit, 1)) * 100);
            return (
              <tr key={e.path} className="border-b last:border-0 dark:border-gray-700">
                <td className="p-3 font-mono text-xs">{e.path}</td>
                <td className="p-3 text-right"><span className={pct > 90 ? "text-red-500 font-bold" : ""}>{e.currentRpm}</span></td>
                <td className="p-3 text-right text-gray-400">{e.limit}</td>
                <td className="p-3 text-right text-green-600">{e.served}</td>
                <td className="p-3 text-right text-red-500">{e.throttled}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
