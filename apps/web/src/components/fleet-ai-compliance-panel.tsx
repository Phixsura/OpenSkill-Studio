"use client";
export function FleetAiCompliancePanel({ audits, passed, failed, frameworks }: { audits: number; passed: number; failed: number; frameworks: string[]; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Compliance</h3>
    <div className="text-sm">{passed}/{audits} passed · {failed} failed · {frameworks.join(", ")}</div>
  </div>);
}
