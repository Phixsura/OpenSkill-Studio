"use client";

interface ConfigDiff { key: string; values: Record<string, unknown>; }
interface ConfigCompareTableProps { environments: string[]; diffs: ConfigDiff[];
  sameCount: number; diffCount: number; identical: boolean; }

export function ConfigCompareTable({ environments, diffs, sameCount, diffCount, identical }: ConfigCompareTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Config Comparison</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{sameCount} same</span>
          <span className={diffCount > 0 ? "text-yellow-600" : "text-green-600"}>{diffCount} different</span>
        </div>
      </div>
      {identical ? (
        <div className="p-4 text-center text-sm text-green-600">✅ All configs identical</div>
      ) : (
        <table className="w-full text-xs">
          <thead><tr className="text-gray-400 border-b dark:border-gray-700">
            <th className="p-2 text-left">Key</th>
            {environments.map(e => <th key={e} className="p-2 text-center">{e}</th>)}
          </tr></thead>
          <tbody>
            {diffs.map(d => (
              <tr key={d.key} className="border-b last:border-0 dark:border-gray-700 bg-yellow-50/50 dark:bg-yellow-900/5">
                <td className="p-2 font-mono font-medium">{d.key}</td>
                {environments.map(env => (
                  <td key={env} className="p-2 text-center font-mono">{String(d.values[env])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
