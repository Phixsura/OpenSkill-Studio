"use client";
interface DepMatrixPanelProps { services: string[]; matrix: Record<string, Record<string, string>>;
  healthPct: number; healthyPairs: number; totalPairs: number; }
const DOT: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", down: "bg-red-500" };
export function DepMatrixPanel({ services, matrix, healthPct, healthyPairs, totalPairs }: DepMatrixPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔲 Dependency Matrix</h3>
        <span className="text-xs text-gray-400">{healthyPairs}/{totalPairs} healthy ({healthPct}%)</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-[10px]">
          <thead><tr><th className="px-2 py-1"></th>
            {services.map(s => <th key={s} className="px-2 py-1 text-gray-400">{s}</th>)}
          </tr></thead>
          <tbody>
            {services.map(src => (
              <tr key={src} className="border-t dark:border-gray-700">
                <td className="px-2 py-1 font-mono font-bold">{src}</td>
                {services.map(dst => (
                  <td key={dst} className="px-2 py-1 text-center">
                    {matrix[src]?.[dst] ? (
                      <span className={`inline-block w-3 h-3 rounded ${DOT[matrix[src][dst]] ?? "bg-gray-300"}`} />
                    ) : <span className="text-gray-300">-</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
