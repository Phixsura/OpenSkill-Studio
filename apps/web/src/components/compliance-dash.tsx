"use client";

interface Violation { policy: string; field: string; severity: string; }
interface ComplianceDashProps { score: number; compliant: number; nonCompliant: number;
  violations: Violation[]; }

export function ComplianceDash({ score, compliant, nonCompliant, violations }: ComplianceDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Compliance</h3>
        <span className={`text-xs font-bold ${score >= 90 ? "text-green-600" : score >= 70 ? "text-yellow-600" : "text-red-500"}`}>
          {score}% score
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Compliant</div><div className="font-bold text-green-600 text-lg">{compliant}</div></div>
        <div><div className="text-gray-400">Non-Compliant</div><div className="font-bold text-red-500 text-lg">{nonCompliant}</div></div>
      </div>
      {violations.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {violations.map((v, i) => (
            <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
              <span>{v.policy} ({v.field})</span>
              <span className={v.severity === "critical" ? "text-red-600 font-bold" : "text-yellow-600"}>{v.severity}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
