"use client";

interface PermRow { resource: string; actions: Record<string, boolean>; }
interface PermissionMatrixGridProps { matrix: PermRow[]; actions: string[];
  coverage: number; onToggle: (resource: string, action: string) => void; }

export function PermissionMatrixGrid({ matrix, actions, coverage, onToggle }: PermissionMatrixGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Permission Matrix</h3>
        <span className="text-xs text-gray-400">{coverage}% coverage</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Resource</th>
          {actions.map(a => <th key={a} className="p-3 text-center capitalize">{a}</th>)}
        </tr></thead>
        <tbody>
          {matrix.map(row => (
            <tr key={row.resource} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 capitalize font-medium">{row.resource}</td>
              {actions.map(a => (
                <td key={a} className="p-3 text-center">
                  <button onClick={() => onToggle(row.resource, a)}
                    className={`w-5 h-5 rounded ${row.actions[a] ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"} text-xs`}>
                    {row.actions[a] ? "✓" : ""}
                  </button>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
