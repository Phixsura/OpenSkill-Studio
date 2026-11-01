"use client";

interface DiffRow { key: string; values: Record<string, string | null>; isMatch: boolean; missingIn: string[]; }
interface ConfigDiffTableProps { rows: DiffRow[]; environments: string[]; mismatches: number; inSync: boolean; }

export function ConfigDiffTable({ rows, environments, mismatches, inSync }: ConfigDiffTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Config Diff</h3>
        <span className={`text-xs ${inSync ? "text-green-600" : "text-yellow-600"}`}>
          {inSync ? "✓ In sync" : `⚠ ${mismatches} differences`}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="px-3 py-2 text-left font-medium">Key</th>
              {environments.map(e => <th key={e} className="px-3 py-2 text-center font-medium">{e}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.key} className={`border-b dark:border-gray-800 ${!r.isMatch ? "bg-yellow-50 dark:bg-yellow-900/5" : ""}`}>
                <td className="px-3 py-2 font-mono text-xs font-medium">{r.key}</td>
                {environments.map(e => (
                  <td key={e} className="px-3 py-2 text-center text-xs font-mono">
                    {r.values[e] != null ? (
                      <span className={!r.isMatch ? "font-medium" : "text-gray-500"}>{r.values[e]}</span>
                    ) : (
                      <span className="text-red-400 italic">missing</span>
                    )}
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
