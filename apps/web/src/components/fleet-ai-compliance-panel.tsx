"use client";
export function FleetAiCompliancePanel({ totalChecks, passing, regulations, audits, compliant }: { totalChecks: number; passing: number; regulations: number; audits: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Compliance</h3>
    <div className="text-sm">{passing}/{totalChecks} passing · {regulations} regulations · {audits} audits</div>
    {compliant && <span className="text-xs text-green-600">✅ Fully compliant</span>}
  </div>);
}
