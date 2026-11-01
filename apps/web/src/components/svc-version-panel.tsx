"use client";
interface VersionRow { service: string; [env: string]: string; }
interface SvcVersionPanelProps { rows: VersionRow[]; envs: string[]; inconsistentCount: number; }
export function SvcVersionPanel({ rows, envs, inconsistentCount }: SvcVersionPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Service Versions</h3>
        <span className={`text-xs ${inconsistentCount > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {inconsistentCount > 0 ? `⚠ ${inconsistentCount} inconsistent` : "✅ All consistent"}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="border-b dark:border-gray-700">
            <th className="px-4 py-2 text-left">Service</th>
            {envs.map(e => <th key={e} className="px-4 py-2 text-left">{e}</th>)}
          </tr></thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.service} className="border-b dark:border-gray-700">
                <td className="px-4 py-1.5 font-mono">{r.service}</td>
                {envs.map(e => <td key={e} className="px-4 py-1.5 text-gray-400">{r[e]}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
