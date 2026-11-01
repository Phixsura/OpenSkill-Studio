"use client";
interface FailedCheck { control: string; finding: string; }
interface ComplianceRptPanelProps { framework: string; score: number; compliant: boolean;
  passed: number; failed: number; failedChecks: FailedCheck[]; }
export function ComplianceRptPanel({ framework, score, compliant, passed, failed, failedChecks }: ComplianceRptPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 {framework} Compliance</h3>
        <span className={`text-xs font-bold ${compliant ? "text-green-600" : "text-red-500"}`}>
          {score}% · {compliant ? "✅ Compliant" : `❌ ${failed} findings`}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Passed</span><div className="font-bold text-green-600 text-lg">{passed}</div></div>
        <div><span className="text-gray-400">Failed</span><div className={`font-bold text-lg ${failed > 0 ? "text-red-500" : "text-gray-400"}`}>{failed}</div></div>
      </div>
      {failedChecks.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {failedChecks.map(f => (
            <div key={f.control} className="px-4 py-1.5 text-xs text-red-600">
              <span className="font-mono">{f.control}</span>: {f.finding}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
