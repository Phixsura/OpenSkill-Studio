"use client";

interface DepResult { name: string; current: string; latest: string; status: string;
  vulnerabilities: { id: string; severity: string }[]; updateAvailable: boolean; }
interface DependencyScannerTableProps { results: DepResult[]; healthDisplay: string; actionRequired: boolean; }

const STATUS_STYLE: Record<string, string> = {
  vulnerable: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  outdated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  unused: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  up_to_date: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export function DependencyScannerTable({ results, healthDisplay, actionRequired }: DependencyScannerTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Dependencies</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{healthDisplay} healthy</span>
          {actionRequired && <span className="text-xs text-red-500">⚠️ Action needed</span>}
        </div>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-left text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3">Package</th><th className="p-3">Current</th>
          <th className="p-3">Latest</th><th className="p-3">Status</th>
        </tr></thead>
        <tbody>
          {results.map(r => (
            <tr key={r.name} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs">{r.name}</td>
              <td className="p-3 text-xs">{r.current}</td>
              <td className="p-3 text-xs">{r.updateAvailable ? <strong>{r.latest}</strong> : r.latest}</td>
              <td className="p-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_STYLE[r.status] || ""}`}>
                  {r.status.replaceAll("_", " ")}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
