"use client";

interface Policy { resource: string; retentionDays: number; action: string; archive: boolean; }
interface Violation { resource: string; recordId: string; ageDays: number; maxDays: number; overdueDays: number; }
interface RetentionPolicyTableProps { policies: Policy[]; violations: Violation[];
  allCompliant: boolean; }

export function RetentionPolicyTable({ policies, violations, allCompliant }: RetentionPolicyTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📅 Data Retention</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${allCompliant ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {allCompliant ? "✅ Compliant" : `⚠️ ${violations.length} violations`}
        </span>
      </div>
      <div className="p-4">
        <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Policies</h4>
        <div className="space-y-1 mb-4">
          {policies.map(p => (
            <div key={p.resource} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
              <span className="font-medium capitalize">{p.resource}</span>
              <span className="text-xs text-gray-400">{p.retentionDays}d · {p.action}{p.archive ? " + archive" : ""}</span>
            </div>
          ))}
        </div>
        {violations.length > 0 && (
          <>
            <h4 className="text-xs font-semibold text-red-500 uppercase mb-2">Violations</h4>
            {violations.map((v, i) => (
              <div key={i} className="text-xs text-red-500 py-0.5">
                {v.resource}/{v.recordId}: {v.ageDays}d old (max {v.maxDays}d, {v.overdueDays}d overdue)
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
