"use client";

interface Violation { resource: string; missingTags: string[]; }
interface TagPolicyPanelProps { total: number; compliant: number; nonCompliant: number;
  compliancePct: number; violations: Violation[]; }

export function TagPolicyPanel({ total, compliant, nonCompliant, compliancePct, violations }: TagPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Tag Policy</h3>
        <span className={`text-xs ${compliancePct === 100 ? "text-green-600" : "text-yellow-600"}`}>
          {compliancePct}% compliant · {compliant}/{total}
        </span>
      </div>
      {violations.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {violations.map(v => (
            <div key={v.resource} className="px-4 py-2 text-xs">
              <span className="font-mono text-red-600">{v.resource}</span>
              <span className="text-gray-400 ml-2">missing: {v.missingTags.join(", ")}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
