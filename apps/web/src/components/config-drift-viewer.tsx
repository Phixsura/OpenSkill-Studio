"use client";

interface Drift { key: string; values: Record<string, unknown>; environments: number; }
interface ConfigDriftViewerProps { drifts: Drift[]; envNames: string[];
  hasDrift: boolean; totalKeys: number; }

export function ConfigDriftViewer({ drifts, envNames, hasDrift, totalKeys }: ConfigDriftViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Config Drift</h3>
        <span className={`text-xs ${hasDrift ? "text-yellow-600" : "text-green-600"}`}>
          {hasDrift ? `⚠ ${drifts.length}/${totalKeys} keys drifted` : "✅ No drift"}
        </span>
      </div>
      {drifts.length > 0 && (
        <table className="w-full text-xs">
          <thead><tr className="text-gray-400 border-b dark:border-gray-700">
            <th className="p-2 text-left">Key</th>
            {envNames.map(e => <th key={e} className="p-2 text-center capitalize">{e}</th>)}
          </tr></thead>
          <tbody>
            {drifts.map(d => (
              <tr key={d.key} className="border-b last:border-0 dark:border-gray-700 bg-yellow-50/50 dark:bg-yellow-900/5">
                <td className="p-2 font-mono font-medium">{d.key}</td>
                {envNames.map(env => {
                  const val = String(d.values[env] ?? "—");
                  return <td key={env} className="p-2 text-center font-mono">{val}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
