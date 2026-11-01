"use client";

interface SvcHealth { service: string; status: string; score: number;
  dimensions: Record<string, boolean>; }
interface SvcHealthMatrixProps { matrix: SvcHealth[]; healthPct: number;
  weakest: string | null; }

export function SvcHealthMatrix({ matrix, healthPct, weakest }: SvcHealthMatrixProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏥 Health Matrix</h3>
        <div className="flex gap-2 text-xs">
          <span className="font-bold">{healthPct}%</span>
          {weakest && <span className="text-red-500">weakest: {weakest}</span>}
        </div>
      </div>
      <table className="w-full text-xs">
        <thead><tr className="text-gray-400 border-b dark:border-gray-700">
          <th className="p-2 text-left">Service</th>
          <th className="p-2 text-center">Uptime</th>
          <th className="p-2 text-center">Latency</th>
          <th className="p-2 text-center">Errors</th>
          <th className="p-2 text-center">CPU</th>
        </tr></thead>
        <tbody>
          {matrix.map(s => (
            <tr key={s.service} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-2 font-mono">{s.service}</td>
              {["uptime", "latency", "errors", "saturation"].map(d => (
                <td key={d} className="p-2 text-center">{s.dimensions[d] ? "✅" : "❌"}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
