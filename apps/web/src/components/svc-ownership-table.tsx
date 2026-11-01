"use client";

interface OwnershipRow { service: string; team: string; oncall: string; runbook: boolean; docs: boolean; }
interface SvcOwnershipTableProps { matrix: OwnershipRow[]; completenessPct: number;
  complete: number; total: number; }

export function SvcOwnershipTable({ matrix, completenessPct, complete, total }: SvcOwnershipTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👤 Service Ownership</h3>
        <span className="text-xs text-gray-400">{complete}/{total} complete ({completenessPct}%)</span>
      </div>
      <table className="w-full text-xs">
        <thead><tr className="text-gray-400 border-b dark:border-gray-700">
          <th className="p-2 text-left">Service</th>
          <th className="p-2 text-left">Team</th>
          <th className="p-2 text-left">On-Call</th>
          <th className="p-2 text-center">Runbook</th>
          <th className="p-2 text-center">Docs</th>
        </tr></thead>
        <tbody>
          {matrix.map(r => (
            <tr key={r.service} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-2 font-mono">{r.service}</td>
              <td className="p-2">{r.team || "—"}</td>
              <td className="p-2">{r.oncall || "—"}</td>
              <td className="p-2 text-center">{r.runbook ? "✅" : "❌"}</td>
              <td className="p-2 text-center">{r.docs ? "✅" : "❌"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
